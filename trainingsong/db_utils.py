import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

# If running locally, load environment variables from .env
if os.environ.get("VERCEL") != "1":
    load_dotenv()

ENCRYPT_KEY = os.environ.get("ENCRYPT_KEY")
if ENCRYPT_KEY is None:
    ENCRYPT_KEY = "mock_key"
f = Fernet(ENCRYPT_KEY.encode())


def encrypt(string):
    return f.encrypt(string.encode()).decode()


def decrypt(string):
    return f.decrypt(string.encode()).decode()
