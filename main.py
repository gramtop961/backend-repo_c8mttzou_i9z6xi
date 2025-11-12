import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Lead, Service, CaseStudy, NewsItem

app = FastAPI(title="Marketing & Satcom Agency API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend running", "version": "1.0.0"}

@app.get("/test")
def test_database():
    """Verify database connectivity and list collections"""
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "collections": []
    }
    try:
        if db is not None:
            status["database"] = "✅ Connected"
            status["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            status["database_name"] = os.getenv("DATABASE_NAME") or "Unknown"
            try:
                status["collections"] = db.list_collection_names()[:10]
            except Exception as e:
                status["database"] = f"⚠️ Connected but error listing collections: {str(e)[:80]}"
    except Exception as e:
        status["database"] = f"❌ Error: {str(e)[:80]}"
    return status

# --------- Seed endpoints (idempotent) ---------
@app.post("/seed/services")
def seed_services():
    """Seed default services for IT and Satcom if none exist"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    existing = list(db["service"].find({}).limit(1))
    if existing:
        return {"seeded": False, "message": "Services already exist"}
    defaults = [
        Service(
            title="Managed IT Services",
            category="IT",
            description="End-to-end monitoring, patching, and support for your infrastructure.",
            features=["24/7 monitoring", "Proactive patching", "SLA-backed support"],
            icon="Server"
        ).model_dump(),
        Service(
            title="Cloud Migration",
            category="IT",
            description="Plan, migrate, and optimize workloads across AWS/Azure/GCP.",
            features=["Assessment", "Lift-and-shift", "Cost optimization"],
            icon="Cloud"
        ).model_dump(),
        Service(
            title="VSAT Deployment",
            category="Satcom",
            description="Reliable satellite internet for remote sites and maritime.",
            features=["Ku/Ka-band", "Global coverage", "Managed service"],
            icon="SatelliteDish"
        ).model_dump(),
        Service(
            title="Emergency Connectivity",
            category="Satcom",
            description="Rapid-deploy terminals for disaster recovery and field ops.",
            features=["Portable terminals", "Rapid setup", "Secure links"],
            icon="Radio"
        ).model_dump(),
    ]
    db["service"].insert_many(defaults)
    return {"seeded": True, "count": len(defaults)}

# --------- Lead endpoints ---------
@app.post("/api/leads")
def create_lead(lead: Lead):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("lead", lead)
    return {"id": inserted_id, "status": "received"}

# --------- Content query endpoints ---------
@app.get("/api/services", response_model=List[Service])
def list_services(category: Optional[str] = None):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filt = {"category": category} if category else {}
    docs = get_documents("service", filt)
    # Normalize ObjectId
    for d in docs:
        d.pop("_id", None)
    return docs

@app.get("/api/news", response_model=List[NewsItem])
def list_news(limit: int = 6):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = list(db["newsitem"].find({}).sort("published_at", -1).limit(limit))
    for d in docs:
        d.pop("_id", None)
    return docs

@app.get("/api/case-studies", response_model=List[CaseStudy])
def list_case_studies(tag: Optional[str] = None, limit: int = 6):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filt = {"tags": tag} if tag else {}
    docs = list(db["casestudy"].find(filt).sort("created_at", -1).limit(limit))
    for d in docs:
        d.pop("_id", None)
    return docs

# Simple health
@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
