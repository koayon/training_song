import databases
import sqlalchemy
from sqlalchemy import Table, Column, String, text
import os
from dotenv import load_dotenv
from typing import Optional, Dict

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

tokens = Table(
        "tokens",
        metadata,
        Column("email", String, primary_key=True, unique=True),
        Column("access_token", String),
        Column("refresh_token", String),
        Column("expires_at", String),
    )

engine = sqlalchemy.create_engine(
        DATABASE_URL
    )

def create() -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS tokens"))
    metadata.create_all(engine)

async def store_tokens(email: str, access_token: str, refresh_token: str, expires_at: str) -> None:
    query = tokens.insert().values(email=email, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)
    await database.execute(query)

async def get_tokens(email: str) -> Optional[Dict[str, str]]:
    query = tokens.select().where(tokens.c.email == email)
    result = await database.fetch_one(query)
    return result
