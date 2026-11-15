from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, dict
from datetime import datetime
from bson import ObjectId
from app.core.database import mongo_db

router = APIRouter(prefix="/vulnerabilidades", tags=["MongoDB - CVEs"])

class VulnCreate(BaseModel):
    cve_id: str
    descripcion: str
    cvss_score: float

class VulnPatch(BaseModel):
    cvss_score: Optional[float] = None

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("", response_model=List[dict])
def get_vulns():
    docs = mongo_db.vulnerabilidades.find({"is_deleted": False})
    return [serialize(d) for d in docs]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_vuln(payload: VulnCreate):
    data = payload.model_dump()
    data["is_deleted"] = False
    data["deleted_at"] = None
    res = mongo_db.vulnerabilidades.insert_one(data)
    data["_id"] = str(res.inserted_id)
    return data

@router.patch("/{id}")
def patch_vuln(id: str, payload: VulnPatch):
    if not payload.cvss_score:
        raise HTTPException(400, "Sin campos a modificar")
    res = mongo_db.vulnerabilidades.find_one_and_update(
        {"_id": ObjectId(id), "is_deleted": False},
        {"$set": {"cvss_score": payload.cvss_score}},
        return_document=True
    )
    if not res:
        raise HTTPException(404, "Vulnerabilidad no encontrada")
    return serialize(res)

@router.delete("/{id}")
def delete_vuln(id: str):
    res = mongo_db.vulnerabilidades.find_one_and_update(
        {"_id": ObjectId(id), "is_deleted": False},
        {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}}
    )
    if not res:
        raise HTTPException(404, "Vulnerabilidad no encontrada")
    return {"message": "Borrado logico exitoso", "id": id}