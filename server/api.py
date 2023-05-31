"""
The main API. It takes in a percentage and returns
the song that was number 1 on the Billboard Hot 100 on that day.
"""

import datetime
import json
from typing import Tuple, Union, Optional
from urllib.error import HTTPError
import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from urllib.parse import unquote

import billboard
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from env_vars import CLIENT_ID, CLIENT_SECRET


@dataclass
class Song:
    artist: str
    weeks: int
    title: str


def main(
    percentage: float,
    chart: str = "hot-100",
) -> Union[Tuple[str, str], None]:
    if percentage > 100 or percentage < 0:
        print("Please enter a percentage between 0 and 100")
        return
    if percentage < 1:
        # Turn a decimal into a percentage
        percentage *= 100

    number_one_song, target_date = get_number_one_song(percentage, chart)

    song_name = number_one_song.title
    artist_name = number_one_song.artist

    print(
        f"The song that was Number 1 {percentage}% through the 1900s was {song_name} by {artist_name}."
    )
    print(
        f"The date was {target_date} and the song was on the chart for {number_one_song.weeks} weeks."
    )
    print(datetime.datetime.now())

    # return percentage, song_name, artist_name, autoplay, target_date

    # try:
    #     sp = authenticate_spotify(spotify_client_id, spotify_client_secret)
    #     # return True
    # except HTTPError as e:
    #     logging.debug(e)
    #     print(
    #         "Please ensure that Spotify is open on your device and you are logged in."
    #     )
    #     print("It may help to play a song on Spotify before trying again.")
    #     raise HTTPException(
    #         status_code=500, detail="Spotify authentication failed"
    #     ) from e

    # # devices = sp.devices()
    # # device_list = devices['devices']

    print("about to call spotify_link")
    return song_name, artist_name


def post_auth(sp, song_name, artist_name, autoplay) -> None:
    link, name, uri = spotify_link(sp, song_name, artist_name)

    print(f"Here's a link to the song {name} on Spotify")
    print(link)
    if autoplay:
        try:
            start_playing_on_spotify(sp, uri)
        except HTTPError as e:
            raise HTTPException(
                status_code=424, detail="Spotify playback failed"
            ) from e

    # TODO: Throw print statements into function calls to clean this up
    # TODO: Spotify describes the song as belonging to these genres:
    # TODO: Genius song description:


def get_number_one_song(
    percentage: float, chart: str = "hot-100"
) -> Tuple[Song, datetime.date]:
    target_year = int(percentage)

    # Calculate the target date based on the fractional part of the percentage
    fractional_percentage = percentage % 1
    days_in_year = (
        365
        if not (
            target_year % 4 == 0 and (target_year % 100 != 0 or target_year % 400 == 0)
        )
        else 366
    )
    target_day = int(days_in_year * fractional_percentage)

    target_date = datetime.date(1900 + target_year, 1, 1) + datetime.timedelta(
        days=target_day
    )

    # Fetch the Billboard Hot 100 chart data for the target date
    chart_output = billboard.ChartData(chart, date=target_date)

    # Get the Number 1 song on the chart
    number_one_song = chart_output[0]

    # TODO: Billboard started in 1958. We need to think of something to do
    # with the years before that
    # Maybe before that date I'll hardcode in a 5 songs for each year and just return a random one?
    # Can have some Easter eggs like Taylor's 22 etc.

    # Maybe add in a random chart mode as well?

    return number_one_song, target_date


def genius_description():
    raise NotImplementedError


def spotify_link(sp, song_name: str, artist_name: str) -> Tuple[str, str, str]:
    """Get the Spotify link for the song using the Spotify API"""
    song = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)["tracks"][
        "items"
    ][0]
    link = song["external_urls"]["spotify"]
    name = song["name"]
    uri = song["uri"]

    return link, name, uri


def start_playing_on_spotify(sp, uri, device_id=None):
    """Start playing song"""
    sp.start_playback(device_id=device_id, uris=[uri])


app = FastAPI()

load_dotenv()  # take environment variables from .env.

# sp_client_id = os.getenv("CLIENT_ID")
# sp_client_secret = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://localhost:8000/api_callback"
# SPOTIFY_REDIRECT_URI = "https://trainingsong-1-h1171059.deta.app/api_callback"
SCOPE = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"


@app.get("/")
async def root(
    p: Union[float, None] = None, chart: str = "hot-100", autoplay: bool = False
):
    if p is None:
        return {"Hello": "World"}
    try:
        song_artist = main(p, chart)
        if song_artist:
            song_name, artist_name = song_artist
        else:
            raise HTTPException(status_code=400, detail="No song found")

        response = authenticate_spotify(song_name, artist_name, autoplay)
        print("authenticated spotify")
        return response

    # return {
    #     "percentage": p,
    #     "chart": chart,
    #     "autoplay": autoplay,
    #     "song_name": song_name,
    #     "artist_name": artist_name,
    # }

    except Exception as e:
        return {"error": "Yo", "exception": str(e)}


def authenticate_spotify(song_name, artist_name, autoplay):
    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
    )

    state_data = {
        "song_name": song_name,
        "artist_name": artist_name,
        "autoplay": autoplay,
    }
    # print(spotify_client_id == os.getenv("CLIENT_ID"))
    auth_url = sp_oauth.get_authorize_url(state=json.dumps(state_data))
    print("auth url", auth_url)
    return RedirectResponse(auth_url)


def create_spotify_client(code):
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
    )

    print("About to get access token")
    # Get the access token
    # token_info = sp_oauth.get_cached_token() or sp_oauth.get_access_token()
    token_info = sp_oauth.get_access_token(code)
    print("Got access token")
    print("token info", token_info)

    if token_info:
        access_token = token_info["access_token"]
    else:
        raise HTTPException(status_code=500, detail="Unable to get access token")

    # Create a Spotify client with the access token
    sp = spotipy.Spotify(auth=access_token)
    return sp


@app.get("/api_callback")
def callback(request: Request):
    print("Hit callback endpoint")
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    print(code)
    print(state)

    if state:
        state = unquote(state)
        state = state.replace("'", '"')
        state = state.replace("+", " ")
        state_data = json.loads(state)
    else:
        raise HTTPException(status_code=500, detail="Unable to parse state data")

    song_name = state_data.get("song_name")
    artist_name = state_data.get("artist_name")
    autoplay = state_data.get("autoplay")

    try:
        sp = create_spotify_client(code)
    except HTTPError as e:
        print(
            "Please ensure that Spotify is open on your device and you are logged in."
        )
        print("It may help to play a song on Spotify before trying again.")
        raise HTTPException(
            status_code=500, detail="Spotify authentication failed"
        ) from e
    try:
        post_auth(sp, song_name, artist_name, autoplay)
    except Exception as e:
        raise HTTPException(status_code=424, detail=str(e)) from e
