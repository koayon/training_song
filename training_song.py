"""Entry point"""

from typing import Union, List, Optional, Tuple, Dict, Any
import requests
from server.spotify import SPOTIFY_REDIRECT_URI

# BASE_URL = "https://trainingsong-1-h1171059.deta.app/"
# BASE_URL = "http://localhost:8000/"


def training_song(
    acc: Union[float, List[float], None],
    chart: Optional[str] = "hot-100",
    autoplay: Optional[bool] = False,
    # ) -> Tuple[Union[float, List[float], None], dict]:
) -> Tuple[Union[float, List[float], None], Dict[str, Any]]:
    """Return the training song for a given percentage"""
    if acc:
        p = acc if isinstance(acc, float) else acc[-1]
    else:
        p = None

    raw_response = requests.get(
        SPOTIFY_REDIRECT_URI,
        params={
            "p": p,
            "autoplay": autoplay,
            "chart": chart,
        },
        timeout=15,
        allow_redirects=True,
    )
    print(raw_response.content)
    response = raw_response.json()

    print("Congrats your model got an accuracy of", p, "percent!")
    try:
        print(response["song_info"])
    except AttributeError:
        print("No song info found")

    return acc, response


if __name__ == "__main__":
    raw_input = input("How well did your model do? (Enter a percentage): ")
    input_percentage = float(raw_input) if raw_input else None
    print()
    training_song(input_percentage)
