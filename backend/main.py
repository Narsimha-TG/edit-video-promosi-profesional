from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="Creación Audiovisual IA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerationRequest(BaseModel):
    title: str
    scene_type: str
    duration_seconds: int
    resolution: str
    model_engine: str

class GenerationStatus(BaseModel):
    id: str
    title: str
    status: str
    score: Optional[float] = None
    timestamp: str

# In-memory store
db = [
    {"id": "1", "title": "Costa Brava Sunset", "status": "completed", "scene_type": "landscape", "duration_seconds": 30, "resolution": "4k", "score": 4.8, "model_engine": "flux-v1", "timestamp": "2023-10-27T10:00:00Z"}
]

@app.get("/api/health")
def health():
    return {"status": "online", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/analytics")
def get_analytics():
    return {"total_generations": len(db), "avg_score": sum(d['score'] for d in db if d['score']) / len(db)}

@app.post("/api/generations/render")
def create_generation(req: GenerationRequest):
    new_gen = {
        "id": str(uuid.uuid4()),
        **req.dict(),
        "status": "processing",
        "score": 0.0,
        "timestamp": datetime.utcnow().isoformat()
    }
    db.append(new_gen)
    return new_gen

@app.get("/api/generations/status")
def get_status(id: str):
    for item in db:
        if item["id"] == id:
            return item
    raise HTTPException(status_code=404, detail="Generation not found")

@app.post("/api/reviews")
def submit_review(id: str, score: float):
    for item in db:
        if item["id"] == id:
            item["score"] = score
            return {"message": "Review updated", "id": id}
    raise HTTPException(status_code=404, detail="Generation not found")