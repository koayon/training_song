from urllib.parse import urlencode, urlunparse

PROD_API = True

OAUTH_CODE = None
if PROD_API:
    URL = "https://training-song-api.vercel.app"
else:
    URL = "https://training-song-api-koayon.vercel.app"

LOCAL_REDIRECT_URI = "http://localhost:8000/local_callback"

CLIENT_ID = "4259770654fb4353813dbf19d8b20608"

AUTH_BASE = "https://accounts.spotify.com/authorize"
SCOPE = "user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-state"
query = urlencode(
    {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": LOCAL_REDIRECT_URI,
        "scope": SCOPE,
    }
)

AUTH_URL = urlunparse(("https", "accounts.spotify.com", "/authorize", "", query, ""))
