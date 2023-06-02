"""Spotify API functions"""

from urllib.error import HTTPError
import json
from typing import Tuple, Union, Optional
from dataclasses import dataclass, asdict

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import RedirectResponse
from fastapi import HTTPException

from env_vars import CLIENT_ID, CLIENT_SECRET

print(CLIENT_ID)

AUTH_SCOPE = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"

PROD = True

if PROD:
    URL = "https://trainingsong-1-h1171059.deta.app"
else:
    URL = "http://localhost:8000"
# SPOTIFY_REDIRECT_URI = f"{URL}/api_callback"
SPOTIFY_REDIRECT_URI = URL


@dataclass
class StateData:
    """Dataclass for authenticate_spotify function"""

    song_name: str
    artist_name: str
    autoplay: Optional[bool]
    song_info: str
    target_date: str
    percentage: float
    chart: str


def authenticate_spotify() -> spotipy.Spotify:
    """Get the Spotify authentication URL"""

    # state_dict = asdict(state_data)
    # auth_url = sp_oauth.get_authorize_url(state=json.dumps(state_dict))
    # return RedirectResponse(auth_url)

    token = spotipy.util.prompt_for_user_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=AUTH_SCOPE,
    )
    sp = spotipy.Spotify(auth=token)
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
