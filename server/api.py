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
    spotify_client_code: str = "",
    # TODO: Make this non-optional
) -> Dict[str, Union[str, bool, float, None]]:
    """The main API endpoint. It takes in a percentage p, interacts with the billboard api and then redirects to the callback for the Spotify API."""

    if p is None:
        return {"hello": "world"}

    try:
        song_results = get_billboard_data(p, chart)
        song_results.autoplay = autoplay
    except HTTPException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    if not spotify_client_code:
        raise HTTPException(status_code=400, detail="Missing Spotify code")

    song_info = song_results.song_info
    target_date = song_results.target_date

    sp = create_spotify_client(spotify_client_code)

    link, _name, uri = spotify_link(
        sp, song_results.song_name, song_results.artist_name
    )

    if autoplay:
        errors = attempt_play(sp, uri)
    else:
        errors = ""

    output = {
        "spotify_link": link,
        "song_name": song_results.song_name,
        "artist_name": song_results.artist_name,
        "target_date": target_date,
        "percentage": song_results.percentage,
        "chart": chart,
        "errors": errors,
        "song_info": song_info,
    }

    return output


def attempt_play(sp, uri):
    "Attempt to play the song on Spotify"
    errors = ""
    devices = sp.devices()
    active_devices = devices["devices"] if devices else None

    if not active_devices:
        errors = "Unable to start playback because there are no active devices available. Please ensure that Spotify is active on one of your devices and try again."
    else:
        try:
            start_playback(sp, uri)

        except HTTPException:
            errors = "Unable to start playback. Please ensure that Spotify is active on one of your devices and try again."
    return errors
