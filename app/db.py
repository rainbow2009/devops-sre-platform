import os
from functools import cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import DeclarativeBase


def required_env(name: str) -> str:
    value = os.getenv(name)

    if not value or value == "REPLACE_WITH_LOCAL_PASSWORD":
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


def get_database_url() -> URL:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    return URL.create(
        drivername="postgresql+psycopg",
        username=required_env("POSTGRES_USER"),
        password=required_env("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=required_env("POSTGRES_DB"),
    )


@cache
def get_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


class Base(DeclarativeBase):
    pass
