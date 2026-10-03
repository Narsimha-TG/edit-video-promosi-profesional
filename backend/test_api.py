import pytest
from fastapi.testclient import TestClient
from backend.main import app, db

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_database():
    """Ensure baseline database state before each test execution."""
    db.clear()
    db.append({
        "id": "1",
        "title": "Costa Brava Sunset",
        "status": "completed",
        "scene_type": "landscape",
        "duration_seconds": 30,
        "resolution": "4k",
        "score": 4.8,
        "model_engine": "flux-v1",
        "timestamp": "2023-10-27T10:00:00Z"
    })

def test_health_check():
    """Test /api/health returns status 200 and expected payload structure."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "online"
    assert "timestamp" in data

def test_analytics_metrics():
    """Test /api/analytics returns aggregated generation metrics."""
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_generations" in data
    assert "avg_score" in data
    assert data["total_generations"] == 1
    assert data["avg_score"] == 4.8

def test_create_generation():
    """Test POST /api/generations/render initiates generative render pipeline."""
    payload = {
        "title": "Picos de Europa Aerial Tour",
        "scene_type": "mountain",
        "duration_seconds": 20,
        "resolution": "4k",
        "model_engine": "flux-v1"
    }
    response = client.post("/api/generations/render", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["scene_type"] == payload["scene_type"]
    assert data["duration_seconds"] == payload["duration_seconds"]
    assert data["resolution"] == payload["resolution"]
    assert data["model_engine"] == payload["model_engine"]
    assert data["status"] == "processing"
    assert data["score"] == 0.0
    assert "timestamp" in data

def test_get_generation_status():
    """Test GET /api/generations/status retrieves generation by ID."""
    response = client.get("/api/generations/status", params={"id": "1"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1"
    assert data["title"] == "Costa Brava Sunset"

def test_get_generation_status_not_found():
    """Test GET /api/generations/status returns 404 for invalid ID."""
    response = client.get("/api/generations/status", params={"id": "non-existent-id"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Generation not found"

def test_submit_review():
    """Test POST /api/reviews updates review score for an existing scene."""
    response = client.post("/api/reviews", params={"id": "1", "score": 4.95})
    assert response.status_code == 200
    assert response.json() == {"message": "Review updated", "id": "1"}
    
    # Verify score updated in store
    status_response = client.get("/api/generations/status", params={"id": "1"})
    assert status_response.status_code == 200
    assert status_response.json()["score"] == 4.95
