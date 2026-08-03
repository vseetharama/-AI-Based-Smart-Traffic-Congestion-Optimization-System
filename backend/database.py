import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv(Path(__file__).resolve().parent / ".env")

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "traffic_system").strip()
MONGODB_TLS = os.getenv("MONGODB_TLS", "true").strip().lower() not in {"false", "0", "no"}
MONGODB_TLS_ALLOW_INVALID_CERTS = os.getenv("MONGODB_TLS_ALLOW_INVALID_CERTS", "true").strip().lower() not in {"false", "0", "no"}

_client: Optional[MongoClient] = None
_database = None


def get_database():
    """Create and return a reusable MongoDB database connection."""
    global _client, _database

    if _database is not None:
        return _database

    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not configured. Please set it in the backend .env file.")

    try:
        client_kwargs = {
            "serverSelectionTimeoutMS": 5000,
            "tls": MONGODB_TLS,
        }
        if MONGODB_TLS_ALLOW_INVALID_CERTS:
            client_kwargs["tlsAllowInvalidCertificates"] = True
        _client = MongoClient(MONGODB_URI, **client_kwargs)
        _database = _client[DATABASE_NAME]
        _client.admin.command("ping")
        print(f"MongoDB Connected Successfully")
        print(f"Database Name: {DATABASE_NAME}")
        return _database
    except PyMongoError as exc:
        print(f"MongoDB Connection Failed: {exc}")
        raise
    except Exception as exc:
        print(f"MongoDB Connection Failed: {exc}")
        raise


def list_collections():
    """Return a list of collections in the configured database."""
    db = get_database()
    return db.list_collection_names()


def get_database_name() -> str:
    """Return the configured database name."""
    return DATABASE_NAME


def close_connection():
    """Close an active MongoDB client connection."""
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None


def insert_verification_document():
    """Insert a single verification document into the configured collection."""
    db = get_database()
    collection = db["traffic_logs"]
    document = {
        "type": "connection_test",
        "message": "MongoDB Connected Successfully",
        "created_at": datetime.now(timezone.utc),
    }
    result = collection.insert_one(document)
    print("Database connected")
    print("Collection ready")
    print("Test document inserted successfully")
    return result.inserted_id
