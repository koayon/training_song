import responses
import datetime

from unittest.mock import patch
import pytest
import billboard

from training_song.server.billboard_io import (
    get_billboard_data,
    get_number_one_song,
    Song,
)


def test_get_billboard_data_invalid_percentage():
    with pytest.raises(ValueError):
        get_billboard_data(101)
    with pytest.raises(ValueError):
        get_billboard_data(-1)
    with pytest.raises(ValueError):
        get_billboard_data(-0.1)


@pytest.mark.parametrize(
    "percentage, expected_song_name, expected_artist_name",
    [
        (75, "Lucy In The Sky With Diamonds", "Elton John"),
    ],
)
@patch("training_song.server.billboard_io.get_number_one_song")
def test_get_billboard_data(
    mock_get_number_one_song, percentage, expected_song_name, expected_artist_name
):
    # Mock the response from get_number_one_song
    mock_song = Song(artist=expected_artist_name, weeks=10, title=expected_song_name)
    mock_date = datetime.date(1975, 1, 1)
    mock_get_number_one_song.return_value = (mock_song, mock_date)

    # Call the function with the test inputs
    result = get_billboard_data(percentage)

    # Verify the function returned the expected result
    assert result.song_name == expected_song_name
    assert result.artist_name == expected_artist_name


@pytest.mark.parametrize(
    "percentage, chart_output, expected_target_date",
    [
        (75.8, [5], datetime.date(1975, 10, 19)),
    ],
)
@patch("billboard.ChartData")
def test_get_number_one_song(
    mock_billboard_ChartData, percentage, chart_output, expected_target_date
):
    mock_billboard_ChartData.return_value = chart_output, expected_target_date
    result = get_number_one_song(percentage=percentage)
    assert result[1] == expected_target_date
