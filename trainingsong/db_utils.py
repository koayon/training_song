import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

# If running locally, load environment variables from .env
if os.environ.get("VERCEL") != "1":
    load_dotenv()

ENCRYPT_KEY = os.environ.get("ENCRYPT_KEY")
MOCK_KEY = "Ev8c4pycMFdhUH7n_ZH__dqR30Nf_iJIbK0Sp2P55Ak="
if ENCRYPT_KEY is None:
    ENCRYPT_KEY = MOCK_KEY
f = Fernet(ENCRYPT_KEY.encode())


def encrypt(string):
    return f.encrypt(string.encode()).decode()


def decrypt(string):
    return f.decrypt(string.encode()).decode()
