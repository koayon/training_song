"""Entry point"""

from typing import Union, List, Optional, Tuple, Dict, Any, NamedTuple
import webbrowser
from threading import Thread
import time

import requests
import uvicorn
from fastapi import FastAPI, Request

URL = "https://training-song-api.vercel.app"

local_app = FastAPI()
OAUTH_CODE = None
# TODO: Search cache for code and use that if it exists?
AUTH_URL = "https://accounts.spotify.com/authorize?client_id=4259770654fb4353813dbf19d8b20608&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Flocal_callback&scope=user-modify-playback-state+user-read-currently-playing+user-read-recently-played+user-read-playback-state"
# TODO: Build this up more sensibly with the given function.
LOCAL_REDIRECT_URI = "http://localhost:8000/local_callback"


def training_song(
    acc: Union[float, List[float], None],
    chart: Optional[str] = "hot-100",
    autoplay: Optional[bool] = False,
    verbose: Optional[bool] = False,
) -> Tuple[Union[float, List[float], None], Dict[str, Any]]:
    """Return the training song for a given percentage
    Outputs: (acc, response)"""

    if acc:
        p = acc if isinstance(acc, (float, int)) else acc[-1]
    else:
        p = None

    params = {
        "p": p,
        "autoplay": autoplay,
        "chart": chart,
        "spotify_client_code": OAUTH_CODE,
    }

    raw_response = requests.get(
        URL,
        params=params,
        timeout=15,
        allow_redirects=True,
    )
    response = raw_response.json()

    if verbose:
        print("Congrats your model got an accuracy of", p, "percent!")
        try:
            print(response["song_info"])
        except AttributeError:
            print("No song info found")

    return acc, response


@local_app.get("/local_callback")
async def spotify_callback(request: Request):
    "Callback for the local server to capture the OAuth code"
    global OAUTH_CODE
    OAUTH_CODE = request.query_params.get("code")
    return "Success! You can close this window."


def start_local_server():
    "Start the local server"
    uvicorn.run(local_app, host="0.0.0.0", port=8000)


def ts(
    input_percentage: float, chart="hot-100", autoplay=False, verbose=False
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

    # start the local server in a new thread
    server_thread = Thread(target=start_local_server)
    server_thread.start()

    # open the authorization URL in a browser
    webbrowser.open(AUTH_URL)

    # wait for the user to authorize and for the server to capture the OAuth code
    while not OAUTH_CODE:
        time.sleep(1)

    # now we can call the training_song function with the captured OAuth code
    acc, response = training_song(
        input_percentage, chart=chart, autoplay=autoplay, verbose=verbose
    )
    return acc, response


if __name__ == "__main__":
    INPUT_PERCENTAGE = None
    RAW_INPUT = ""
    while not INPUT_PERCENTAGE:
        RAW_INPUT = input("How well did your model do? (Enter a percentage): ")
    INPUT_PERCENTAGE = float(RAW_INPUT)

    ts(INPUT_PERCENTAGE)
