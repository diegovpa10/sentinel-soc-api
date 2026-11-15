import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.database import redis_client

router = APIRouter(prefix="/sesiones", tags=["Redis - Sesiones"])

class SesionCreate(BaseModel):
    token: str
    analista_id: str

class SesionPatch(BaseModel):
    analista_id: Optional[str] = None

@router.get("", response_model=List[dict])
def get_sesiones():
    keys = redis_client.keys("session:*")
    activas = []
    for k in keys:
        item = json.loads(redis_client.get(k))
        if not item.get("is_deleted", False):
            activas.append(item)
    return activas

@router.post("", status_code=status.HTTP_201_CREATED)
def create_sesion(payload: SesionCreate):
    key = f"session:{payload.token}"
    data = {
        "token": payload.token,
        "analista_id": payload.analista_id,
        "is_deleted": False,
        "deleted_at": None
    }
    redis_client.set(key, json.dumps(data))
    return data

@router.patch("/{token}")
def patch_sesion(token: str, payload: SesionPatch):
    key = f"session:{token}"
    raw = redis_client.get(key)
    if not raw:
        raise HTTPException(404, "Sesion no encontrada")
    item = json.loads(raw)
    if item.get("is_deleted"):
        raise HTTPException(404, "Sesion inactiva")
    
    if payload.analista_id:
        item["analista_id"] = payload.analista_id
    redis_client.set(key, json.dumps(item))
    return item

@router.delete("/{token}")
def delete_sesion(token: str):
    key = f"session:{token}"
    raw = redis_client.get(key)
    if not raw:
        raise HTTPException(404, "Sesion no encontrada")
    item = json.loads(raw)
    item["is_deleted"] = True
    item["deleted_at"] = datetime.utcnow().isoformat()
    redis_client.set(key, json.dumps(item))
    return {"message": "Borrado logico exitoso", "token": token}