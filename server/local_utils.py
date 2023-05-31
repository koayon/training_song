"""Utility functions for the API"""
from urllib.parse import unquote
import json

from fastapi import HTTPException


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
