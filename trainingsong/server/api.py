"""
Main API file.
"""

from typing import Union, Dict
import webbrowser

from fastapi import FastAPI, HTTPException, Query

from trainingsong.server.billboard_io import get_billboard_data
from trainingsong.server.spotify import (
    create_spotify_client,
    spotify_link,
    start_playback,
)
from trainingsong.server.db import get_tokens, database_session

app = FastAPI()


@app.get("/")
async def root(
    email: str,
    spotify_client_code: Union[str, None] = None,
    p: float = Query(..., ge=0, le=100),
    chart: str = "hot-100",
    autoplay: bool = False,
) -> Dict[str, Union[str, bool, float, None]]:
    """The main API endpoint. It takes in a percentage p, interacts with the billboard api and then redirects to the callback for the Spotify API."""

    print("Hit root endpoint")

    try:
        song_results = get_billboard_data(p, chart)
        song_results.autoplay = autoplay
    except HTTPException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    if not spotify_client_code and not email:
        raise HTTPException(status_code=400, detail="Missing Spotify code and email")

    print("Got spotify code")

    song_info = song_results.song_info
    target_date = song_results.target_date

    try:
        if spotify_client_code is None and email is None:
            raise HTTPException(
                status_code=400, detail="Missing Spotify code and email"
            )
        sp = await create_spotify_client(spotify_client_code, email)
    except HTTPException as e:
        # raise HTTPException(
        #     status_code=404, detail=f"str(e). Failed to created Spotify client"
        # ) from e
        return {"errors": f"str(e). Failed to created Spotify client"}

    print(sp)

    link, _name, uri = spotify_link(
        sp, song_results.song_name, song_results.artist_name
    )

    print(link)

    print(uri)

    if autoplay:
        errors = attempt_play(sp, uri)
        if errors:
            errors += "Failed to start playback"
            webbrowser.open(link)
    else:
        errors = ""
        webbrowser.open(link)

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


@app.get("/hello")
async def hello():
    return {"hello": "world"}


@app.get("/email_in_db")
async def email_in_db(email: str) -> Dict[str, bool]:
    async with database_session() as session:
        result = await get_tokens(email)
    return {"present_in_db": result is not None}


def attempt_play(sp, uri) -> str:
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
