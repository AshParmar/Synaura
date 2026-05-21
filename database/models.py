# database/models.py
"""
Document schemas (as TypedDicts) for MongoDB collections.

Collections:
  - users        → one document per authenticated user
  - scan_reports → one document per AI-generated radiology report
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import TypedDict


class UserDocument(TypedDict, total=False):
    """Schema for the `users` collection."""
    _id: str                   # Clerk user ID (string)
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
    report_count: int


class ScanReportDocument(TypedDict, total=False):
    """Schema for the `scan_reports` collection."""
    _id: str                   # auto-generated ObjectId (str representation)
    user_id: str               # Clerk user ID — links to users._id
    original_filename: str
    disease: str
    confidence: float
    interval: list[float]      # [lower, upper] fuzzy interval
    region: str
    report: str                # full markdown report text
    heatmap_base64: str        # base64-encoded GradCAM PNG
    gcs_url: str | None        # Google Cloud Storage URL for the original scan
    created_at: datetime


def new_scan_report(
    *,
    user_id: str,
    filename: str,
    disease: str,
    confidence: float,
    interval: list[float],
    region: str,
    report: str,
    heatmap_base64: str,
    gcs_url: str | None = None,
) -> ScanReportDocument:
    """Convenience factory that stamps timestamps automatically."""
    return ScanReportDocument(
        user_id=user_id,
        original_filename=filename,
        disease=disease,
        confidence=confidence,
        interval=interval,
        region=region,
        report=report,
        heatmap_base64=heatmap_base64,
        gcs_url=gcs_url,
        created_at=datetime.now(timezone.utc),
    )
