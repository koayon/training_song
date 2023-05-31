"""
The get_billboard_data API. It takes in a percentage and returns
the song that was number 1 on the Billboard Hot 100 on that day.
"""

import datetime
import json
from typing import Tuple, Union
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.parse import unquote

import billboard
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from env_vars import CLIENT_ID, CLIENT_SECRET

SCOPE = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"
PROD = False

if PROD:
    SPOTIFY_REDIRECT_URI = "https://trainingsong-1-h1171059.deta.app/api_callback"
else:
    SPOTIFY_REDIRECT_URI = "http://localhost:8000/api_callback"


@dataclass
class Song:
    """A dataclass to store the song name, artist name and number of weeks on the chart"""

    artist: str
    weeks: int
    title: str


def get_billboard_data(
    percentage: float,
    chart: str = "hot-100",
) -> Tuple[str, str, str]:
    """Call Billboard API and get the song name, artist name and song info"""
    if percentage > 100 or percentage < 0:
        raise HTTPException(
            status_code=400, detail="Please enter a percentage between 0 and 100"
        )
    if percentage < 1:
        # Turn a decimal into a percentage
        percentage *= 100

    number_one_song, target_date = get_number_one_song(percentage, chart)

    song_name = number_one_song.title
    artist_name = number_one_song.artist

    song_info = f"""The Number 1 song {percentage}% through the 1900s on the {chart} chart was {song_name} by {artist_name}. \n The date was {target_date} and the song was on the chart for {number_one_song.weeks} weeks."""
    return song_name, artist_name, song_info


def start_playback(sp, uri, device_id=None) -> None:
    """Start playing the song on Spotify"""
    try:
        sp.start_playback(device_id=device_id, uris=[uri])
    except HTTPError as e:
        raise HTTPException(status_code=424, detail="Spotify playback failed") from e


def get_number_one_song(
    percentage: float, chart: str = "hot-100"
) -> Tuple[Song, datetime.date]:
    """Get the number one song on the chosen Billboard chart on date that is percentage% through the 1900s"""
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

    return number_one_song, target_date


def spotify_link(sp, song_name: str, artist_name: str) -> Tuple[str, str, str]:
    """Get the Spotify link for the song using the Spotify API"""
    song = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)["tracks"][
        "items"
    ][0]
    link = song["external_urls"]["spotify"]
    name = song["name"]
    uri = song["uri"]

    return link, name, uri


app = FastAPI()


@app.get("/")
async def root(
    p: Union[float, None] = None,
    chart: str = "hot-100",
    autoplay: bool = False,
):
    """The main API endpoint. It takes in a percentage p, interacts with the billboard api and then redirects to the callback for the Spotify API."""
    if p is None:
        return {"Hello": "World"}
    try:
        song_results = get_billboard_data(p, chart)
        if song_results:
            song_name, artist_name, song_info = song_results
        else:
            raise HTTPException(status_code=400, detail="No song found")

        response = authenticate_spotify(song_name, artist_name, autoplay, song_info)
        return response

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/api_callback")
def callback(request: Request):
    """The callback for the Spotify API once we've authenticated. Gets the song link and plays it if autoplay was selected. Then returns the song info to the endpoint."""
    spotify_client_code = request.query_params.get("code")
    state_data = request.query_params.get("state")
    try:
        song_name, artist_name, autoplay, song_info = parse_state_data(state_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        sp = create_spotify_client(spotify_client_code)
    except HTTPError as e:
        raise HTTPException(
            status_code=400, detail="Spotify client authentication failed"
        ) from e

    link, _name, uri = spotify_link(sp, song_name, artist_name)
    errors = None

    if autoplay:
        try:
            start_playback(sp, uri)

        except Exception:
            errors = "Unable to start playback. Please ensure that Spotify is active on one of your devices and try again."

    return {
        "spotify_link": link,
        "song_info": song_info,
        "song_name": song_name,
        "artist_name": artist_name,
        #  "target_date": target_date
        #  "percentage": percentage,
        # "chart": chart
        "errors": errors,
    }


def parse_state_data(state):
    """Parse the state data from the Spotify API callback"""
    if state:
        state = unquote(state)
        state = state.replace("+", " ")
        state_data = json.loads(state)
    else:
        raise HTTPException(status_code=500, detail="Unable to parse state data")

    song_name = state_data.get("song_name")
    artist_name = state_data.get("artist_name")
    autoplay = state_data.get("autoplay")
    song_info = state_data.get("song_info")
    return song_name, artist_name, autoplay, song_info


def authenticate_spotify(song_name, artist_name, autoplay, song_info):
    """Get the Spotify authentication URL"""

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
        "song_info": song_info,
    }
    auth_url = sp_oauth.get_authorize_url(state=json.dumps(state_data))
    return RedirectResponse(auth_url)


def create_spotify_client(code):
    """Create a Spotify client using the code from the Spotify API callback"""

    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
    )

    # Get the access token
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info["access_token"] if token_info else None

    # Create a Spotify client with the access token
    sp = spotipy.Spotify(auth=access_token)
    return sp
