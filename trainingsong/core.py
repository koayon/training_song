"""Entry point"""

import json
import os
import re
import time
import webbrowser
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
import uvicorn
from fastapi import FastAPI, Request

from trainingsong.ts_utils import AUTH_URL, OAUTH_CODE, URL


def _training_song(
    p: float,
    chart: Optional[str] = "hot-100",
    autoplay: Optional[bool] = True,
    verbose: Optional[bool] = True,
    email: Optional[str] = None,
    metric: Optional[str] = "accuracy",
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

    response = raw_response.json()

    if verbose:
        print(f"Congrats your model's {metric} was ", p, "%!")
        if response and "song_info" in response:
            print(response["song_info"])
        else:
            print("No song info found")
    if "errors" in response:
        print(response["errors"])

    if "open_link" in response and response["open_link"]:
        webbrowser.open(response["spotify_link"])

    return p, response


def ts(
    input_percentage: Union[float, List[float]],
    chart: str = "hot-100",
    autoplay: bool = True,
    verbose: bool = True,
    metric: str = "accuracy",
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

    email = _get_email()
    if not email:
        set_email()
        email = _get_email()

    if not email:
        raise ValueError(
            "No email found. Please run from the command line or add an email to a .email file in the root directory to proceed. "
        )

    email_in_db = _check_email(email)

    if not email_in_db:
        # start the local server in a new thread
        if not OAUTH_CODE:
            server_thread = Thread(target=_start_local_server)
            server_thread.start()

            webbrowser.open(AUTH_URL)

            # wait for the user to authorize and for the server to capture the OAuth code
            while not OAUTH_CODE:
                time.sleep(0.5)

    # if the input percentage is a list, we want to take the final value
    accuracy = (
        input_percentage
        if isinstance(input_percentage, (float, int))
        else input_percentage[-1]
    )

    acc, response = _training_song(
        accuracy,
        chart=chart,
        autoplay=autoplay,
        verbose=verbose,
        email=email,
        metric=metric,
    )
    if not email_in_db:
        print(
            """

Thanks for using Training Song!
For your first time, we used a local server to listen for your Spotify authorisation code.
You can exit this process now.
For future uses an access token is stored securely."""
        )
    return acc, response


local_app = FastAPI()


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


def _is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def set_email():
    email_address = None
    while not email_address:
        potential_email = input("Enter your email address: ")
        if _is_valid_email(potential_email):
            email_address = potential_email
        else:
            print("Invalid email address. Please try again.")
    with open(".email", "w") as f:
        json.dump({"email": email_address}, f)


def _get_email():
    if not os.path.exists(".email"):
        return None
    with open(".email", "r") as f:
        try:
            email_dict = json.load(f)
        except json.decoder.JSONDecodeError:
            email_dict = {"email": None}
    return email_dict["email"]


def _check_email(email: str) -> str:
    "Returns truthy string if email is in db"
    response = requests.get(URL + "/email_in_db", params={"email": email})
    if response and (response.status_code == 200):
        return response.json()["present_in_db"]
    else:
        raise ValueError("Error checking email")


if __name__ == "__main__":
    INPUT_PERCENTAGE = None
    RAW_INPUT = ""
    while not INPUT_PERCENTAGE:
        RAW_INPUT = input("How well did your model do? (Enter a percentage): ")
        if RAW_INPUT.isdigit():
            INPUT_PERCENTAGE = float(RAW_INPUT)

    ts(INPUT_PERCENTAGE, verbose=True, autoplay=True)
