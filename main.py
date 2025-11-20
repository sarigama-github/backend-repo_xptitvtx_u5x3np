import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Recipe, Lesson, Ad, Video, Contact

app = FastAPI(title="Culinary Educational API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to convert ObjectId to string for JSON responses

def serialize_doc(doc: dict):
    if not doc:
        return doc
    d = {**doc}
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # convert datetime to isoformat if present
    for k, v in list(d.items()):
        try:
            import datetime
            if isinstance(v, (datetime.datetime, datetime.date)):
                d[k] = v.isoformat()
        except Exception:
            pass
    return d

@app.get("/")
def read_root():
    return {"message": "Culinary Educational Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Insertion endpoints

@app.post("/api/recipes")
def create_recipe(payload: Recipe):
    new_id = create_document("recipe", payload)
    return {"id": new_id}

@app.post("/api/lessons")
def create_lesson(payload: Lesson):
    new_id = create_document("lesson", payload)
    return {"id": new_id}

@app.post("/api/ads")
def create_ad(payload: Ad):
    new_id = create_document("ad", payload)
    return {"id": new_id}

@app.post("/api/videos")
def create_video(payload: Video):
    new_id = create_document("video", payload)
    return {"id": new_id}

@app.post("/api/contact")
def set_contact(payload: Contact):
    # store single contact doc; upsert behavior
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    from datetime import datetime, timezone
    data = payload.model_dump()
    data['updated_at'] = datetime.now(timezone.utc)
    existing = db["contact"].find_one({})
    if existing:
        db["contact"].update_one({"_id": existing["_id"]}, {"$set": data})
        return {"id": str(existing["_id"]) }
    else:
        inserted_id = create_document("contact", payload)
        return {"id": inserted_id}

# Query/search endpoints

@app.get("/api/recipes")
def list_recipes(q: Optional[str] = Query(None, description="Search query"), tag: Optional[str] = None):
    filter_dict = {}
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"ingredients": {"$elemMatch": {"$regex": q, "$options": "i"}}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}}
        ]
    if tag:
        filter_dict.setdefault("tags", {"$elemMatch": {"$regex": tag, "$options": "i"}})
    items = [serialize_doc(d) for d in get_documents("recipe", filter_dict)]
    return {"items": items}

@app.get("/api/lessons")
def list_lessons(q: Optional[str] = Query(None)):
    filter_dict = {}
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}}
        ]
    items = [serialize_doc(d) for d in get_documents("lesson", filter_dict)]
    return {"items": items}

@app.get("/api/ads")
def list_ads(active: Optional[bool] = True):
    filter_dict = {}
    if active is not None:
        filter_dict["active"] = active
    items = [serialize_doc(d) for d in get_documents("ad", filter_dict)]
    return {"items": items}

@app.get("/api/videos")
def list_videos(q: Optional[str] = Query(None)):
    filter_dict = {}
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}}
        ]
    items = [serialize_doc(d) for d in get_documents("video", filter_dict)]
    return {"items": items}

@app.get("/api/contact")
def get_contact():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    doc = db["contact"].find_one({})
    return serialize_doc(doc) if doc else {}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
