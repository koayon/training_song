"""Spotify API functions"""

from urllib.error import HTTPError
from typing import Tuple, Union, Optional
from dataclasses import dataclass
import os
import json
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import HTTPException
from db.db import store_tokens, get_tokens, update_tokens, database_session

SCOPE = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"

PROD = True

if PROD:
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
else:
    from env_vars import CLIENT_ID, CLIENT_SECRET
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

    async with database_session() as session:
        token_info = await get_tokens(email)

        if not token_info:
            print("Getting access token...")
            # Get the access token
            if code is None:
                raise ValueError("No code provided")
            try:
                token_info = sp_oauth.get_access_token(code)
            except:
                raise HTTPException(status_code=400, detail="Invalid Spotify code")
            if not token_info:
                raise HTTPException(status_code=400, detail="Invalid Spotify code")

            # Put token info into sqlalchemy database
            await store_tokens(
                email,
                token_info["access_token"],
                token_info["refresh_token"],
                token_info["expires_at"],
            )

        # If the access token is expired, refresh it
        if token_info["expires_at"] < time.time():
            print("Refreshing access token...")
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

            if token_info:
                # Put token info into sqlalchemy database
                await update_tokens(
                    email,
                    token_info["access_token"],
                    token_info["refresh_token"],
                    token_info["expires_at"],
                )
            else:
                raise ValueError("Failed to refresh access token. Please try again. ")

    access_token = token_info["access_token"] if token_info else None

    print("Got access token!")

    # Create a Spotify client with the access token
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
    except HTTPError as e:
        raise HTTPException(status_code=424, detail="Spotify playback failed") from e
