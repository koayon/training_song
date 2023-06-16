"""Database module for storing and retrieving user tokens from database."""
import os
from contextlib import contextmanager
from functools import lru_cache

import sqlalchemy
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import BigInteger, Column, String, Table, create_engine
from sqlalchemy.orm import sessionmaker

# If running locally, load environment variables from .env
if os.environ.get("VERCEL") != "1":
    load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set or empty")

ENCRYPT_KEY = os.environ.get("ENCRYPT_KEY")
if ENCRYPT_KEY is None:
    raise ValueError("ENCRYPT_KEY environment variable not set or empty")
else:
    f = Fernet(ENCRYPT_KEY.encode())

engine = create_engine(DATABASE_URL, future=True)
Session = sessionmaker(bind=engine)

metadata = sqlalchemy.MetaData()
tokens = Table(
    "tokens",
    metadata,
    Column("email", String, primary_key=True, unique=True),
    Column("access_token", String),
    Column("refresh_token", String),
    Column("expires_at", BigInteger),
)


def store_tokens(email, access_token, refresh_token, expires_at, f=f):
    with engine.connect() as connection:
        query = tokens.insert().values(
            email=email,
            access_token=f.encrypt(access_token.encode()).decode(),
            refresh_token=f.encrypt(refresh_token.encode()).decode(),
            expires_at=expires_at,
        )
        connection.execute(query)
        connection.commit()


@lru_cache(maxsize=1)
def get_tokens(email):
    with engine.connect() as connection:
        query = tokens.select().where(tokens.c.email == email)
        result = connection.execute(query).fetchone()
        if result:
            result = dict(result)
            result["access_token"] = f.decrypt(result["access_token"]).decode()
            result["refresh_token"] = f.decrypt(result["refresh_token"]).decode()
        return result


def update_tokens(email, access_token, refresh_token, expires_at, f=f):
    with engine.connect() as connection:
        query = (
            tokens.update()
            .where(tokens.c.email == email)
            .values(
                access_token=f.encrypt(access_token).decode(),
                refresh_token=f.encrypt(refresh_token).decode(),
                expires_at=expires_at,
            )
        )
        connection.execute(query)
        connection.commit()


def delete_tokens(email):
    with engine.connect() as connection:
        query = tokens.delete().where(tokens.c.email == email)
        connection.execute(query)
        connection.commit()


def create():
    check = input("Are you sure you want to drop the database? (y/n) ")
    if check != "y":
        return print("Aborting")

    with engine.connect() as connection:
        connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS tokens"))
    metadata.create_all(engine)
    print("Created fresh database")


@contextmanager
def database_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def main():
    pass


if __name__ == "__main__":
    main()
