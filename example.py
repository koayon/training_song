"""Example of using the API."""

import requests
import uvicorn

PROD = False
# PORT = 8000

uvicorn.run("server.api:app", host="0.0.0.0")

if PROD:
    URL = "https://trainingsong-1-h1171059.deta.app/"
else:
    URL = "http://localhost:8000/"

# payload = {"p": 0.8}
# response = requests.get(URL, data=payload, timeout=5)

p = 0.8
response = requests.get(f"{URL}?p={p}", timeout=15)

print(response.status_code)
print(response.json())
print()
