"Billboard API calls and data processing"

import datetime
from dataclasses import dataclass
from typing import Tuple

import billboard
from fastapi import HTTPException

from trainingsong.server.spotify import StateData


@dataclass
class Song:
    """A dataclass to store the song name, artist name and number of weeks on the chart"""

    artist: str
    weeks: int
    title: str


def get_billboard_data(
    percentage: float,
    chart: str = "hot-100",
) -> StateData:
    """Call Billboard API and get the song name, artist name and song info"""
    if percentage > 100 or percentage < 0:
        raise ValueError("Please enter a percentage between 0 and 100")

    try:
        number_one_song, target_date = get_number_one_song(percentage, chart)
    except HTTPException:
        raise HTTPException(status_code=404, detail="No chart data found")

    song_name = number_one_song.title
    artist_name = number_one_song.artist

    song_info = f"""The Number 1 song {percentage}% through the 1900s on the {chart} chart was {song_name} by {artist_name}. \nThe date was {target_date} and the song was on the chart for {number_one_song.weeks} weeks."""
    result = StateData(
        song_name=song_name,
        artist_name=artist_name,
        autoplay=None,
        song_info=song_info,
        target_date=str(target_date),
        percentage=percentage,
        chart=chart,
    )
    return result


def get_number_one_song(
    percentage: float, chart: str = "hot-100"
) -> Tuple[Song, datetime.date]:
    """Get the number one song on the chosen Billboard chart on date that is percentage% through the 1900s"""
    target_year = int(percentage)

    # Calculate the target date based on the fractional part of the percentage
    fractional_percentage = percentage % 1
    days_in_year = (
        366
        if target_year % 4 == 0 and (target_year % 100 != 0 or target_year % 400 == 0)
        else 365
    )
    target_day = int(days_in_year * fractional_percentage)

    target_date = datetime.date(1900 + target_year, 1, 1) + datetime.timedelta(
        days=target_day
    )

    chart_output = billboard.ChartData(chart, date=target_date)

    if chart_output:
        number_one_song = chart_output[0]
    else:
        raise HTTPException(status_code=404, detail="No chart data found")

    return number_one_song, target_date
