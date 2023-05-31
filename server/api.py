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

import billboard
from fastapi import FastAPI, HTTPException
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
    spotify_client_id,
    spotify_client_secret,
    percentage: float,
    chart: str = "hot-100",
    autoplay: bool = True,
) -> None:
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

    try:
        sp = authenticate_spotify(spotify_client_id, spotify_client_secret)
        # return True
    except HTTPError as e:
        logging.debug(e)
        print(
            "Please ensure that Spotify is open on your device and you are logged in."
        )
        print("It may help to play a song on Spotify before trying again.")
        raise HTTPException(
            status_code=500, detail="Spotify authentication failed"
        ) from e

    # # devices = sp.devices()
    # # device_list = devices['devices']

    print("about to call spotify_link")

    link, name, uri = spotify_link(sp, song_name, artist_name)

    print(f"Here's a link to the song {name} on Spotify")
    print(link)
    if autoplay:
        start_playing_on_spotify(sp, uri)

    # TODO: Throw print statements into function calls to clean this up
    # TODO: Spotify describes the song as belonging to these genres:
    # TODO: Genius song description:


def authenticate_spotify(spotify_client_id, spotify_client_secret):
    # spotify_client_id = CLIENT_ID
    # spotify_client_secret = CLIENT_SECRET
    # spotify_redirect_uri = "http://localhost:8000"
    spotify_redirect_uri = "https://trainingsong-1-h1171059.deta.app/"
    scope = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"

    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri=spotify_redirect_uri,
        scope=scope,
    )
    print(spotify_client_id)

    # Get the access token
    # token_info = sp_oauth.get_cached_token() or sp_oauth.get_access_token()
    print("About to get access token")
    token_info = sp_oauth.get_access_token()
    print("Got access token")
    print("token info", token_info)
    if token_info:
        access_token = token_info["access_token"]
    else:
        raise HTTPException(status_code=500, detail="Unable to get access token")

    # Create a Spotify client with the access token
    sp = spotipy.Spotify(auth=access_token)

    return sp


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


@app.get("/")
async def root(
    p: Union[float, None] = None, chart: str = "hot-100", autoplay: bool = False
):
    spotify_client_id = CLIENT_ID
    spotify_client_secret = CLIENT_SECRET

    if p is None:
        return {"Hello": "World"}
    try:
        main(spotify_client_id, spotify_client_secret, p, chart, autoplay)
        RedirectResponse(url="/static/index.html")
        return {"percentage": p, "chart": chart, "autoplay": autoplay}
    except Exception as e:
        return {"error": "Yo", "exception": str(e)}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico")
async def favicon():
    return {"file": "static/favicon.ico"}


@app.get("/login")
def login():
    sp_oauth = spotipy.SpotifyOAuth(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="your_redirect_uri",
        scope="required_scopes",
        cache_path=None,
    )
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)


@app.get("/callback/{code}")
def callback(code: str):
    sp_oauth = spotipy.SpotifyOAuth(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="your_redirect_uri",
        scope="required_scopes",
        cache_path=None,
    )
    # code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    if token_info:
        access_token = token_info["access_token"]
    else:
        raise HTTPException(status_code=500, detail="Unable to get access token")
    # Store the access token somewhere (like a session)
    # Then, redirect the user wherever you like
    return RedirectResponse("/some-page-in-your-app")


# @app.get("/")
# async def root():
#     return {"Hello": "World"}
