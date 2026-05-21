# database/crud.py
"""
CRUD operations for MongoDB collections.

All functions are synchronous (PyMongo).
If you need async routes, swap PyMongo for Motor and use `await`.
"""

from __future__ import annotations
from bson import ObjectId
from datetime import datetime, timezone
from pymongo import DESCENDING

from database.mongo_client import get_db
from database.models import ScanReportDocument, UserDocument, new_scan_report


# ── Scan Reports ──────────────────────────────────────────────────────────────

def save_scan_report(doc: ScanReportDocument) -> str:
    """
    Insert a scan report into the `scan_reports` collection.

    Returns the inserted document ID as a string.
    """
    db = get_db()
    result = db["scan_reports"].insert_one(dict(doc))
    return str(result.inserted_id)


def get_report_by_id(report_id: str) -> ScanReportDocument | None:
    """Fetch a single report by its ObjectId string."""
    db = get_db()
    doc = db["scan_reports"].find_one({"_id": ObjectId(report_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc  # type: ignore[return-value]


def get_reports_for_user(user_id: str, limit: int = 20) -> list[ScanReportDocument]:
    """
    Fetch the most recent `limit` reports for a given user.
    Sorted newest-first.
    """
    db = get_db()
    cursor = (
        db["scan_reports"]
        .find({"user_id": user_id})
        .sort("created_at", DESCENDING)
        .limit(limit)
    )
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results  # type: ignore[return-value]


def delete_report(report_id: str) -> bool:
    """Delete a report by ID. Returns True if a document was deleted."""
    db = get_db()
    result = db["scan_reports"].delete_one({"_id": ObjectId(report_id)})
    return result.deleted_count > 0


# ── Users ─────────────────────────────────────────────────────────────────────

def upsert_user(user_id: str, email: str, name: str) -> None:
    """
    Create or update a user document.
    Called after successful Clerk authentication.
    """
    db = get_db()
    db["users"].update_one(
        {"_id": user_id},
        {
            "$set": {"email": email, "name": name, "updated_at": datetime.now(timezone.utc)},
            "$setOnInsert": {"created_at": datetime.now(timezone.utc), "report_count": 0},
        },
        upsert=True,
    )


def increment_report_count(user_id: str) -> None:
    """Atomically increment the report counter for a user."""
    db = get_db()
    db["users"].update_one({"_id": user_id}, {"$inc": {"report_count": 1}})


def get_user(user_id: str) -> UserDocument | None:
    """Fetch a user document by Clerk user ID."""
    db = get_db()
    doc = db["users"].find_one({"_id": user_id})
    return doc  # type: ignore[return-value]
