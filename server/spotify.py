"""Spotify API functions"""

from urllib.error import HTTPError
import json
from typing import Tuple

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import RedirectResponse
from fastapi import HTTPException

from env_vars import CLIENT_ID, CLIENT_SECRET

SCOPE = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"

PROD = False

if PROD:
    SPOTIFY_REDIRECT_URI = "https://trainingsong-1-h1171059.deta.app/api_callback"
else:
    SPOTIFY_REDIRECT_URI = "http://localhost:8000/api_callback"


def authenticate_spotify(
    song_name, artist_name, autoplay, song_info, target_date, percentage, chart
):
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
        "target_date": target_date,
        "percentage": percentage,
        "chart": chart,
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


def spotify_link(sp, song_name: str, artist_name: str) -> Tuple[str, str, str]:
    """Get the Spotify link for the song using the Spotify API"""
    song = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)["tracks"][
        "items"
    ][0]
    link = song["external_urls"]["spotify"]
    name = song["name"]
    uri = song["uri"]

    return link, name, uri


def start_playback(sp, uri, device_id=None) -> None:
    """Start playing the song on Spotify"""
    try:
        sp.start_playback(device_id=device_id, uris=[uri])
    except HTTPError as e:
        raise HTTPException(status_code=424, detail="Spotify playback failed") from e
