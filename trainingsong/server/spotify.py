"""Spotify API functions"""

import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple, Union
from urllib.error import HTTPError

import spotipy
from dotenv import load_dotenv
from fastapi import HTTPException
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from trainingsong.server.db import (
    database_session,
    get_tokens,
    store_tokens,
    update_tokens,
)

SCOPE = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"

# If running locally, load environment variables from .env
if os.environ.get("VERCEL") != "1":
    load_dotenv()


CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

SPOTIFY_REDIRECT_URI = "http://localhost:8000/local_callback"


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


async def create_spotify_client(code: Union[str, None], email: str) -> spotipy.Spotify:
    """Create a Spotify client using the code from the Spotify API callback"""

    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
    )

    with database_session() as session:
        token_info = get_tokens(email)

        if not token_info:
            print("Getting access token...")
            if code is None:
                raise ValueError("No code provided")
            try:
                token_info = sp_oauth.get_access_token(code)
            except:
                raise HTTPException(status_code=400, detail="Invalid Spotify code")
            if not token_info:
                raise HTTPException(status_code=400, detail="Invalid Spotify code")

            store_tokens(
                email,
                token_info["access_token"],
                token_info["refresh_token"],
                token_info["expires_at"],
            )

        if token_info["expires_at"] < time.time():
            print("Refreshing access token...")
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

            if token_info:
                update_tokens(
                    email,
                    token_info["access_token"],
                    token_info["refresh_token"],
                    token_info["expires_at"],
                )
            else:
                raise ValueError("Failed to refresh access token. Please try again. ")

    access_token = token_info["access_token"] if token_info else None

    print("Got access token!")

    sp = spotipy.Spotify(auth=access_token)
    print("Created Spotify client")

    return sp


def spotify_link(
    sp: spotipy.Spotify, song_name: str, artist_name: str
) -> Tuple[str, str, str]:
    """Get the Spotify link for the song using the Spotify API"""
    search_result = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)
    if search_result:
        song = search_result["tracks"]["items"][0]
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Song {song_name} by {artist_name} not found on Spotify",
        )

    link = song["external_urls"]["spotify"]
    name = song["name"]
    uri = song["uri"]

    return link, name, uri


def start_playback(sp, uri, device_id=None) -> None:
    """Start playing the song on Spotify"""
    try:
        sp.start_playback(device_id=device_id, uris=[uri])
    except (HTTPError, SpotifyException) as e:
        ValueError(f"Spotify playback failed: {e}")
