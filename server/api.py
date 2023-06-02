"""
The get_billboard_data API. It takes in a percentage and returns
the song that was number 1 on the Billboard Hot 100 on that day.
"""

from typing import Union, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from ts_utils import parse_state_data
from billboard_io import get_billboard_data
from spotify import (
    authenticate_spotify,
    spotify_link,
    start_playback,
)

app = FastAPI()


@app.get("/")
async def root(
    p: Union[float, None] = None,
    chart: str = "hot-100",
    autoplay: bool = False,
) -> Dict[str, Union[str, bool, float, None]]:
    """The main API endpoint. It takes in a percentage p, interacts with the billboard api and then redirects to the callback for the Spotify API."""

    print("Started!")

    if p is None:
        return {"hello": "world"}
    try:
        song_results = get_billboard_data(p, chart)
        song_results.autoplay = autoplay

        print("Got song results! About to authenticate Spotify...")
        sp = authenticate_spotify()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    song_name = song_results.song_name
    artist_name = song_results.artist_name
    target_date = song_results.target_date
    percentage = song_results.percentage
    song_info = song_results.song_info

    print("About to get Spotify link...")

    link, _name, uri = spotify_link(sp, song_name, artist_name)
    errors = ""

    print("Got Spotify link, about to start playback")

    devices = sp.devices()
    active_devices = devices["devices"] if devices else None

    if autoplay:
        if not active_devices:
            errors = "Unable to start playback because there are no active devices available. Please ensure that Spotify is active on one of your devices and try again."

        try:
            start_playback(sp, uri)
        except Exception:
            pass

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
