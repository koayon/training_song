"""Entry point"""

from typing import Union, List, Optional, Tuple, Dict, Any
import requests
import time
import webbrowser
from threading import Thread

import uvicorn
from fastapi import FastAPI, Request
from spotipy.oauth2 import SpotifyOAuth

from server.spotify import URL
from server.spotify import CLIENT_ID, CLIENT_SECRET, SCOPE

local_app = FastAPI()
OAUTH_CODE = None
LOCAL_REDIRECT_URI = "http://localhost:8000/local_callback"


def training_song(
    acc: Union[float, List[float], None],
    chart: Optional[str] = "hot-100",
    autoplay: Optional[bool] = False,
    # ) -> Tuple[Union[float, List[float], None], dict]:
) -> Tuple[Union[float, List[float], None], Dict[str, Any]]:
    """Return the training song for a given percentage"""

    if acc:
        p = acc if isinstance(acc, float) else acc[-1]
    else:
        p = None

    params = {
        "p": p,
        "autoplay": autoplay,
        "chart": chart,
        "code": OAUTH_CODE,
    }

    raw_response = requests.get(
        URL,
        params=params,
        timeout=15,
        allow_redirects=True,
    )

    print(raw_response.content)
    response = raw_response.json()

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
    print(f"Captured OAuth code: {OAUTH_CODE}")
    return "Success! You can close this window."


def start_local_server():
    uvicorn.run(local_app, host="0.0.0.0", port=8000)


def authorize():
    """Get the Spotify authentication URL and open it in a browser"""
    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=LOCAL_REDIRECT_URI,
        scope=SCOPE,
    )
    auth_url = sp_oauth.get_authorize_url()
    webbrowser.open(auth_url)


if __name__ == "__main__":
    raw_input = input("How well did your model do? (Enter a percentage): ")
    input_percentage = float(raw_input) if raw_input else None

    # start the local server in a new thread
    server_thread = Thread(target=start_local_server)
    server_thread.start()

    # open the authorization URL in a browser
    authorize()

    # wait for the user to authorize and for the server to capture the OAuth code
    while not OAUTH_CODE:
        time.sleep(1)

    # now we can call the training_song function with the captured OAuth code
    training_song(input_percentage)

    print()
    training_song(input_percentage)

    # When you're done, you can stop the local server
    # Note: Uvicorn doesn't officially support programmatically stopping the server yet,
    # you may have to manually stop the server by interrupting the process (Ctrl+C)
