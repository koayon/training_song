"""
Main API file.
"""

from typing import Union, Dict

from fastapi import FastAPI, HTTPException

from billboard_io import get_billboard_data
from spotify import (
    create_spotify_client,
    spotify_link,
    start_playback,
)

app = FastAPI()


@app.get("/")
async def root(
    p: Union[float, None] = None,
    chart: str = "hot-100",
    autoplay: bool = False,
    code: str = "",
) -> Dict[str, Union[str, bool, float, None]]:
    """The main API endpoint. It takes in a percentage p, interacts with the billboard api and then redirects to the callback for the Spotify API."""

    if p is None:
        return {"hello": "world"}
    try:
        song_results = get_billboard_data(p, chart)
        song_results.autoplay = autoplay
    except HTTPException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    if code:
        spotify_client_code = code
    else:
        spotify_client_code = None
        # Really we want to request a code if we're actually calling this locally???

    state_data = song_results
    if not spotify_client_code or not state_data:
        raise HTTPException(status_code=400, detail="Missing Spotify code or state")

    song_name = state_data.song_name
    artist_name = state_data.artist_name
    autoplay = state_data.autoplay is True
    song_info = state_data.song_info
    target_date = state_data.target_date
    percentage = state_data.percentage
    chart = state_data.chart

    sp = create_spotify_client(spotify_client_code)

    link, _name, uri = spotify_link(sp, song_name, artist_name)
    errors = None

    if autoplay:
        try:
            start_playback(sp, uri)

        except HTTPException:
            errors = "Unable to start playback. Please ensure that Spotify is active on one of your devices and try again."

    return {
        "spotify_link": link,
        "song_name": song_name,
        "artist_name": artist_name,
        "target_date": target_date,
        "percentage": percentage,
        "chart": chart,
        "errors": errors,
        "song_info": song_info,
    }


@app.get("/hello")
async def hello() -> Dict[str, str]:
    """Hello world"""

    return {"Hello": "World"}
