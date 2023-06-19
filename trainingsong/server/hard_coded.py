from trainingsong.server.spotify import StateData


def hard_coded_song(percentage, chart):
    # return get_billboard_data(p, "hot-100")
    p = int(percentage)
    if p in HARD_CODED_DICT:
        song_name = HARD_CODED_DICT[p][0]
        artist_name = HARD_CODED_DICT[p][1]
    else:
        song_name = "Never Gonna Give You Up"
        artist_name = "Rick Astley"

    return StateData(
        song_name=song_name,
        artist_name=artist_name,
        autoplay=None,
        song_info=f"Your results were before the {chart} chart started in {CHART_START_YEAR}. Here's {song_name} by {artist_name} instead.",
        target_date="",
        percentage=percentage,
        chart="",
    )


HARD_CODED_DICT = {
    0: ["Flight of the Bumblebee", "Nikolai Rimsky-Korsakov"],
    1: ["Number 1", "Tinchy Stryder"],
    2: ["The Entertainer", "Scott Joplin"],
    4: ["I'm A Yankee Doodle Dandy", "George M. Cohan"],
    5: ["5 Years Time", "Noah and the Whale"],
    7: ["7 Years", "Lukas Graham"],
    13: ["Rite of Spring", "Igor Stravinsky"],
    21: ["Someone Like You", "Adele"],
    22: ["22", "Taylor Swift"],
    24: ["24K Magic", "Bruno Mars"],
    42: ["42", "Coldplay"],
}

CHART_START_YEAR = 1952
