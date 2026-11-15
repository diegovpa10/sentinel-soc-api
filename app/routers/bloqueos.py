import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.database import redis_client

router = APIRouter(prefix="/bloqueos", tags=["Redis - Bloqueos IPs"])

class BloqueoCreate(BaseModel):
    ip_amenaza: str
    motivo: str

class BloqueoPatch(BaseModel):
    motivo: Optional[str] = None

@router.get("", response_model=List[dict])
def get_bloqueos():
    keys = redis_client.keys("block:*")
    activos = []
    for k in keys:
        item = json.loads(redis_client.get(k))
        if not item.get("is_deleted", False):
            activos.append(item)
    return activos

@router.post("", status_code=status.HTTP_201_CREATED)
def create_bloqueo(payload: BloqueoCreate):
    key = f"block:{payload.ip_amenaza}"
    data = {
        "ip_amenaza": payload.ip_amenaza,
        "motivo": payload.motivo,
        "is_deleted": False,
        "deleted_at": None
    }
    redis_client.set(key, json.dumps(data))
    return data

@router.patch("/{ip}")
def patch_bloqueo(ip: str, payload: BloqueoPatch):
    key = f"block:{ip}"
    raw = redis_client.get(key)
    if not raw:
        raise HTTPException(404, "IP no encontrada")
    item = json.loads(raw)
    if item.get("is_deleted"):
        raise HTTPException(404, "Bloqueo inactivo")
    
    if payload.motivo:
        item["motivo"] = payload.motivo
    redis_client.set(key, json.dumps(item))
    return item

@router.delete("/{ip}")
def delete_bloqueo(ip: str):
    key = f"block:{ip}"
    raw = redis_client.get(key)
    if not raw:
        raise HTTPException(404, "IP no encontrada")
    item = json.loads(raw)
    item["is_deleted"] = True
    item["deleted_at"] = datetime.utcnow().isoformat()
    redis_client.set(key, json.dumps(item))
    return {"message": "Borrado logico exitoso", "ip": ip}