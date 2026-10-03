from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="Edit Video Promosi Profesional API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoJob(BaseModel):
    id: str
    title: str
    status: str
    score: float
    timestamp: str
    render_url: Optional[str] = None
    project_metadata: dict

# In-memory storage
jobs = {
    "job-123": {"id": "job-123", "title": "Promo Summer", "status": "completed", "score": 95.5, "timestamp": datetime.now().isoformat(), "render_url": "https://cdn.example.com/v1.mp4", "project_metadata": {"resolution": "1080p"}}
}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/analytics")
def get_analytics():
    return {"total_jobs": len(jobs), "avg_score": 95.5}

@app.post("/api/reviews")
def submit_review(data: dict):
    return {"message": "Review received", "data": data}

@app.post("/api/render/queue")
def queue_render(payload: dict):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"id": job_id, "title": payload.get("title", "New Project"), "status": "queued", "score": 0.0, "timestamp": datetime.now().isoformat(), "project_metadata": payload}
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/render/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]