import datetime
from typing import Tuple
from dataclasses import dataclass

import billboard

from spotify import StateData


@dataclass
class Song:
    """A dataclass to store the song name, artist name and number of weeks on the chart"""

    artist: str
    weeks: int
    title: str


# TODO: Put in some error handling


def get_billboard_data(
    percentage: float,
    chart: str = "hot-100",
) -> StateData:
    """Call Billboard API and get the song name, artist name and song info"""
    if percentage > 100 or percentage < 0:
        raise ValueError("Please enter a percentage between 0 and 100")
    if percentage < 1:
        # Turn a decimal into a percentage
        percentage *= 100

    number_one_song, target_date = get_number_one_song(percentage, chart)

    song_name = number_one_song.title
    artist_name = number_one_song.artist

    song_info = f"""The Number 1 song {percentage}% through the 1900s on the {chart} chart was {song_name} by {artist_name}. \n The date was {target_date} and the song was on the chart for {number_one_song.weeks} weeks."""
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

    # Fetch the Billboard Hot 100 chart data for the target date
    chart_output = billboard.ChartData(chart, date=target_date)

    # Get the Number 1 song on the chart
    number_one_song = chart_output[0]

    # TODO: Billboard started in 1958. We need to think of something to do
    # with the years before that
    # Maybe before that date I'll hardcode in a 5 songs for each year and just return a random one?
    # Can have some Easter eggs like Taylor's 22 etc.

    return number_one_song, target_date
