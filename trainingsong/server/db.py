"""Database module for storing and retrieving user tokens from database."""

import asyncio
import os
from contextlib import asynccontextmanager

import databases
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import BigInteger, Column, String, Table, text

# If running locally, load environment variables from .env
if os.environ.get("VERCEL") != "1":
    load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set or empty")

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

tokens = Table(
    "tokens",
    metadata,
    Column("email", String, primary_key=True, unique=True),
    Column("access_token", String),
    Column("refresh_token", String),
    Column("expires_at", BigInteger),
)

engine = sqlalchemy.create_engine(DATABASE_URL)


def create() -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS tokens"))
    metadata.create_all(engine)


async def store_tokens(
    email: str, access_token: str, refresh_token: str, expires_at: int
) -> None:
    query = tokens.insert().values(
        email=email,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )
    await database.execute(query)


async def get_tokens(email: str):
    # Return type is dictionary like. It's a Record object from databases
    query = tokens.select().where(tokens.c.email == email)
    result = await database.fetch_one(query)
    return result


async def delete_tokens(email: str) -> None:
    query = tokens.delete().where(tokens.c.email == email)
    await database.execute(query)


async def update_tokens(
    email: str, access_token: str, refresh_token: str, expires_at: int
) -> None:
    query = (
        tokens.update()
        .where(tokens.c.email == email)
        .values(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
    )
    await database.execute(query)


@asynccontextmanager
async def database_session():
    await database.connect()
    try:
        yield
    finally:
        await database.disconnect()


async def main():
    async with database_session():
        pass


if __name__ == "__main__":
    asyncio.run(main())
