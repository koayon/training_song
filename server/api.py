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
    create_spotify_client,
    authenticate_spotify,
    spotify_link,
    start_playback,
    URL,
)

app = FastAPI()


@app.get("/")
async def root(
    p: Union[float, None] = None,
    chart: str = "hot-100",
    autoplay: bool = False,
) -> RedirectResponse:
    """The main API endpoint. It takes in a percentage p, interacts with the billboard api and then redirects to the callback for the Spotify API."""

    if p is None:
        return RedirectResponse(f"{URL}/hello")
    try:
        song_results = get_billboard_data(p, chart)
        song_results.autoplay = autoplay

        redirect_with_state = authenticate_spotify(state_data=song_results)
        return redirect_with_state

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/api_callback")
def callback(request: Request) -> Dict[str, Union[str, bool, float, None]]:
    """The callback for the Spotify API once we've authenticated. Gets the song link and plays it if autoplay was selected. Then returns the song info to the endpoint."""

    spotify_client_code = request.query_params.get("code")
    state_data = request.query_params.get("state")
    if not spotify_client_code or not state_data:
        raise HTTPException(status_code=400, detail="Missing Spotify code or state")

    (
        song_name,
        artist_name,
        autoplay,
        song_info,
        target_date,
        percentage,
        chart,
    ) = parse_state_data(state_data)

    sp = create_spotify_client(spotify_client_code)

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


@app.get("/hello")
async def hello() -> Dict[str, str]:
    """Hello world"""

    return {"Hello": "World"}
