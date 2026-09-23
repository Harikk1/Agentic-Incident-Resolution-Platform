import os
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

_mongo_client = None
_mongo_db = None
_is_connected = False

def get_mongo_db():
    global _mongo_client, _mongo_db, _is_connected
    if settings.MOCK_DATABASE:
        return None

    if _is_connected and _mongo_db is not None:
        return _mongo_db

    try:
        from pymongo import MongoClient
        _mongo_client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=1500)
        # Test connection
        _mongo_client.admin.command('ping')
        _mongo_db = _mongo_client.get_database()
        _is_connected = True
        logger.info("Successfully connected to MongoDB", extra={"uri": settings.MONGODB_URI})
        return _mongo_db
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Falling back to In-Memory Repository.", extra={"mock_database": True})
        _is_connected = False
        return None

def is_mongo_available() -> bool:
    return not settings.MOCK_DATABASE and _is_connected
