"""Entry point"""

from typing import Union, List, Optional, Tuple, Dict, Any, NamedTuple
import webbrowser
from threading import Thread
import time
import json
import os
import re

import asyncio
import requests
import uvicorn
from fastapi import FastAPI, Request

from training_song.server.db.db import get_tokens, database_session

OAUTH_CODE = None
URL = "https://training-song-api-koayon.vercel.app"
local_app = FastAPI()
AUTH_URL = "https://accounts.spotify.com/authorize?client_id=4259770654fb4353813dbf19d8b20608&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Flocal_callback&scope=user-modify-playback-state+user-read-currently-playing+user-read-recently-played+user-read-playback-state"
# TODO: Build this up more sensibly with the given function.
LOCAL_REDIRECT_URI = "http://localhost:8000/local_callback"


def _training_song(
    p: float,
    chart: Optional[str] = "hot-100",
    autoplay: Optional[bool] = True,
    verbose: Optional[bool] = True,
    email: Optional[str] = None,
) -> Tuple[Union[float, List[float], None], Dict[str, Any]]:
    """Return the training song for a given percentage
    Outputs: (acc, response)"""

    params = {
        "p": p,
        "autoplay": autoplay,
        "chart": chart,
        "spotify_client_code": OAUTH_CODE,
        "email": email,
    }

    raw_response = requests.get(
        URL,
        params=params,
        timeout=15,
    )

    print(raw_response.url)

    response = raw_response.json()

    if verbose:
        print("Congrats your model got an accuracy of", p, "percent!")
        if response and "song_info" in response:
            print(response["song_info"])
        else:
            print("No song info found")

    return p, response


async def ts(
    input_percentage: Union[float, List[float]],
    chart="hot-100",
    autoplay=False,
    verbose=False,
) -> Tuple[Union[float, List[float], None], Dict[str, Any]]:
    """Training song function.
    Starts a local server to capture the auth code from spotify and returns the song for your training accuracy.

    Args:
    input_percentage (float): The accuracy of your model.
    chart (str): The chart to use. Defaults to "hot-100".
    autoplay (bool): Whether to autoplay the song. Defaults to False.
    verbose (bool): Whether to print the song info. Defaults to False.

    Outputs:
    acc: The accuracy of your model. In the same form as you put it in.
    response: The response from the server as a dictionary.
    """

    email = get_email()
    if not email:
        # set_email()
        # email = get_email()
        raise ValueError(
            "No email found. Please run from the command line or add an email to a .email file in the root directory to proceed. "
        )

    email_in_db = await check_email(email)

    if not email_in_db:
        # start the local server in a new thread
        if not OAUTH_CODE:
            server_thread = Thread(target=_start_local_server)
            server_thread.start()

            # open the authorization URL in a browser
            webbrowser.open(AUTH_URL)

            # wait for the user to authorize and for the server to capture the OAuth code
            while not OAUTH_CODE:
                time.sleep(1)

    accuracy = (
        input_percentage
        if isinstance(input_percentage, (float, int))
        else input_percentage[-1]
    )

    # now we can call the training_song function with the captured OAuth code
    acc, response = _training_song(
        accuracy, chart=chart, autoplay=autoplay, verbose=verbose, email=email
    )
    return acc, response


@local_app.get("/local_callback")
async def spotify_callback(request: Request):
    "Callback for the local server to capture the OAuth code"
    global OAUTH_CODE
    OAUTH_CODE = request.query_params.get("code")
    print("Got code:", OAUTH_CODE)
    return "Success! You can close this window."


def _start_local_server():
    "Start the local server"
    uvicorn.run(local_app, host="0.0.0.0", port=8000)


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def set_email():
    email_address = None
    while not email_address:
        potential_email = input("Enter your email address: ")
        if is_valid_email(potential_email):
            email_address = potential_email
    with open(".email", "w") as f:
        json.dump({"email": email_address}, f)


def get_email():
    if not os.path.exists(".email"):
        return None
    with open(".email", "r") as f:
        try:
            email_dict = json.load(f)
        except json.decoder.JSONDecodeError:
            email_dict = {"email": None}
    return email_dict["email"]


async def check_email(email):
    async with database_session() as session:
        result = await get_tokens(email)
    return result is not None


if __name__ == "__main__":
    email = get_email()
    if not email:
        set_email()

    INPUT_PERCENTAGE = None
    RAW_INPUT = ""
    # while not INPUT_PERCENTAGE:
    RAW_INPUT = input("How well did your model do? (Enter a percentage): ")
    INPUT_PERCENTAGE = float(RAW_INPUT)

    asyncio.run(ts(INPUT_PERCENTAGE, verbose=True))
