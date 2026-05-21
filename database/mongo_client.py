# database/mongo_client.py
"""
MongoDB Atlas connection singleton.
Uses MONGODB_URI from environment — set this in .env (see .env.example).
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return (and lazily create) the global MongoClient."""
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise EnvironmentError(
                "MONGODB_URI is not set. Copy .env.example → .env and fill in your Atlas connection string."
            )
        _client = MongoClient(uri)
    return _client


def get_db(db_name: str = "synaura") -> Database:
    """Return the Synaura database."""
    return get_client()[db_name]
