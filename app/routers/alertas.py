from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import mongo_db

router = APIRouter(prefix="/alertas", tags=["MongoDB - Alertas IDS"])

class AlertaCreate(BaseModel):
    regla_id: str
    ip_origen: str
    ip_destino: str
    metadatos: Dict[str, Any]

class AlertaPatch(BaseModel):
    metadatos: Optional[Dict[str, Any]] = None

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("", response_model=List[dict])
def get_alertas():
    docs = mongo_db.alertas.find({"is_deleted": False})
    return [serialize(d) for d in docs]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_alerta(payload: AlertaCreate):
    data = payload.model_dump()
    data["is_deleted"] = False
    data["deleted_at"] = None
    res = mongo_db.alertas.insert_one(data)
    data["_id"] = str(res.inserted_id)
    return data

@router.patch("/{id}")
def patch_alerta(id: str, payload: AlertaPatch):
    if not payload.metadatos:
        raise HTTPException(400, "Sin campos a modificar")
    res = mongo_db.alertas.find_one_and_update(
        {"_id": ObjectId(id), "is_deleted": False},
        {"$set": {"metadatos": payload.metadatos}},
        return_document=True
    )
    if not res:
        raise HTTPException(404, "Alerta no encontrada")
    return serialize(res)

@router.delete("/{id}")
def delete_alerta(id: str):
    res = mongo_db.alertas.find_one_and_update(
        {"_id": ObjectId(id), "is_deleted": False},
        {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}}
    )
    if not res:
        raise HTTPException(404, "Alerta no encontrada")
    return {"message": "Borrado logico exitoso", "id": id}