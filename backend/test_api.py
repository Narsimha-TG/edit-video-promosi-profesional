import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_analytics():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    assert "total_jobs" in response.json()
    assert "avg_score" in response.json()

def test_submit_review():
    payload = {"rating": 5, "comment": "Great service"}
    response = client.post("/api/reviews", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Review received"

def test_queue_render_and_status():
    # Test POST /api/render/queue
    payload = {"title": "Test Video", "resolution": "4k"}
    response = client.post("/api/render/queue", json=payload)
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    assert job_id is not None

    # Test GET /api/render/status/{job_id}
    status_response = client.get(f"/api/render/status/{job_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["id"] == job_id
    assert data["status"] == "queued"
    assert data["title"] == "Test Video"