import pytest
from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "retrieval_mode" in data


def test_ask_requires_question():
    resp = client.post("/ask", json={"question": "ab"})
    assert resp.status_code == 422
