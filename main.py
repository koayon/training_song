import requests

URL = "http://localhost:8000/"

# payload = {"p": 0.8}
# response = requests.get(URL, data=payload, timeout=5)

p = 0.8
response = requests.get(f"{URL}?p={p}", timeout=5)

print(response.status_code)
print(response.json())
