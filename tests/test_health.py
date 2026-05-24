# tests/test_health.py
"""
Smoke tests for the Synaura FastAPI backend.
Run with: pytest tests/ -v

These tests do NOT require external API keys — they test the /health endpoint
and basic import structure.
"""

import importlib
import pytest
from fastapi.testclient import TestClient

# Patch env so cloud integrations don't fail to import
import os
os.environ.setdefault("GROQ_API_KEY", "test_key")


@pytest.fixture(scope="module")
def client():
    """Create a test client from the FastAPI app."""
    # Lazy import after env is patched
    from backend.main import app
    return TestClient(app)


def test_health_endpoint(client):
    """/health returns 200 and correct JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data





def test_database_module_imports():
    """database.mongo_client and database.crud import cleanly."""
    try:
        importlib.import_module("database.mongo_client")
        importlib.import_module("database.crud")
        importlib.import_module("database.models")
    except ImportError as e:
        pytest.fail(f"Database module import failed: {e}")


def test_vector_store_module_imports():
    """vector_store modules import cleanly (no Pinecone connection needed for import)."""
    try:
        importlib.import_module("vector_store.pinecone_client")
        importlib.import_module("vector_store.pinecone_retriever")
    except ImportError as e:
        pytest.fail(f"vector_store module import failed: {e}")
