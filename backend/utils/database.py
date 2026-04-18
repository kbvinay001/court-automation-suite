"""
Database utility - MongoDB connection and operations using Motor (async driver).
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase  # type: ignore[import-not-found]
from typing import Optional

logger = logging.getLogger(__name__)

# Database singleton
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "court_automation")


async def init_db():
    """Initialize MongoDB connection and create indexes."""
    global _client, _db
    try:
        _client = AsyncIOMotorClient(
            MONGO_URL,
            serverSelectionTimeoutMS=3000,  # fail fast if DB unavailable
            connectTimeoutMS=3000,
        )
        _db = _client[DB_NAME]

        # Create indexes for common queries
        await _db.cases.create_index("case_number", unique=True)
        await _db.cases.create_index("status")
        await _db.cases.create_index("next_hearing_date")
        await _db.cases.create_index("court_name")
        await _db.cases.create_index([("petitioner", "text"), ("respondent", "text")])

        await _db.causelists.create_index([("court_name", 1), ("date", 1)])
        await _db.causelists.create_index("date")

        await _db.users.create_index("email", unique=True)
        await _db.users.create_index("phone")

        logger.info(f"✅ Connected to MongoDB: {DB_NAME}")
    except Exception as e:
        logger.warning(
            f"⚠ MongoDB unavailable — starting in DEGRADED mode (DB features disabled): {e}"
        )
        _client = None
        _db = None
        # Do NOT raise — allow the server to start without DB


async def close_db():
    """Close MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")


def get_db() -> Optional[AsyncIOMotorDatabase]:
    """Get database instance."""
    return _db


async def get_collection(name: str):
    """Get a specific collection."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db[name]


async def insert_one(collection: str, document: dict) -> str:
    """Insert a document and return its ID."""
    db = get_db()
    if db is None:
        raise RuntimeError("Database not initialized")
    result = await db[collection].insert_one(document)
    return str(result.inserted_id)


async def find_one(collection: str, query: dict) -> Optional[dict]:
    """Find a single document."""
    db = get_db()
    if db is None:
        raise RuntimeError("Database not initialized")
    doc = await db[collection].find_one(query)
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def find_many(collection: str, query: dict, skip: int = 0,
                    limit: int = 20, sort: Optional[list] = None) -> list:
    """Find multiple documents with pagination."""
    db = get_db()
    if db is None:
        raise RuntimeError("Database not initialized")
    cursor = db[collection].find(query).skip(skip).limit(limit)
    if sort:
        cursor = cursor.sort(sort)
    docs = await cursor.to_list(length=limit)
    for doc in docs:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return docs


async def update_one(collection: str, query: dict, update: dict) -> bool:
    """Update a single document."""
    db = get_db()
    if db is None:
        raise RuntimeError("Database not initialized")
    result = await db[collection].update_one(query, {"$set": update})
    return result.modified_count > 0


async def count_documents(collection: str, query: dict) -> int:
    """Count matching documents."""
    db = get_db()
    if db is None:
        raise RuntimeError("Database not initialized")
    return await db[collection].count_documents(query)


async def delete_one(collection: str, query: dict) -> bool:
    """Delete a single document."""
    db = get_db()
    if db is None:
        raise RuntimeError("Database not initialized")
    result = await db[collection].delete_one(query)
    return result.deleted_count > 0


async def aggregate(collection: str, pipeline: list) -> list:
    """Run an aggregation pipeline."""
    db = get_db()
    if db is None:
        raise RuntimeError("Database not initialized")
    cursor = db[collection].aggregate(pipeline)
    return await cursor.to_list(length=None)
