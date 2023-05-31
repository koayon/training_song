"""
The get_billboard_data API. It takes in a percentage and returns
the song that was number 1 on the Billboard Hot 100 on that day.
"""

from typing import Union
from urllib.error import HTTPError

from fastapi import FastAPI, HTTPException, Request
from local_utils import parse_state_data
from billboard_io import get_billboard_data
from spotify import (
    create_spotify_client,
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
):
    """The main API endpoint. It takes in a percentage p, interacts with the billboard api and then redirects to the callback for the Spotify API."""

    if p is None:
        return {"Hello": "World"}
    try:
        song_results = get_billboard_data(p, chart)
        if song_results:
            (
                song_name,
                artist_name,
                song_info,
                target_date,
                percentage,
                chart,
            ) = song_results
        else:
            raise HTTPException(status_code=400, detail="No song found")

        response = authenticate_spotify(
            song_name,
            artist_name,
            autoplay,
            song_info,
            str(target_date),
            percentage,
            chart,
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/api_callback")
def callback(request: Request):
    """The callback for the Spotify API once we've authenticated. Gets the song link and plays it if autoplay was selected. Then returns the song info to the endpoint."""

    spotify_client_code = request.query_params.get("code")
    state_data = request.query_params.get("state")
    try:
        (
            song_name,
            artist_name,
            autoplay,
            song_info,
            target_date,
            percentage,
            chart,
        ) = parse_state_data(state_data)
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
        "song_name": song_name,
        "artist_name": artist_name,
        "target_date": target_date,
        "percentage": percentage,
        "chart": chart,
        "errors": errors,
        "song_info": song_info,
    }
