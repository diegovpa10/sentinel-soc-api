from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.core.database import get_pg_connection

router = APIRouter(prefix="/activos", tags=["PostgreSQL - Activos"])

class ActivoCreate(BaseModel):
    hostname: str
    ip_address: str
    tipo: str
    criticidad: str

class ActivoPatch(BaseModel):
    criticidad: Optional[str] = None

@router.get("", response_model=List[dict])
def get_activos():
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM activos WHERE is_deleted = FALSE;")
        datos = cur.fetchall()
    conn.close()
    return datos

@router.post("", status_code=status.HTTP_201_CREATED)
def create_activo(payload: ActivoCreate):
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO activos (hostname, ip_address, tipo, criticidad)
            VALUES (%s, %s, %s, %s) RETURNING *;
        """, (payload.hostname, payload.ip_address, payload.tipo, payload.criticidad))
        nuevo = cur.fetchone()
        conn.commit()
    conn.close()
    return nuevo

@router.patch("/{id}")
def patch_activo(id: int, payload: ActivoPatch):
    if not payload.criticidad:
        raise HTTPException(status_code=400, detail="Sin campos a modificar")
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE activos SET criticidad = %s WHERE id = %s AND is_deleted = FALSE RETURNING *;", (payload.criticidad, id))
        actualizado = cur.fetchone()
        conn.commit()
    conn.close()
    if not actualizado:
        raise HTTPException(404, "Activo no encontrado")
    return actualizado

@router.delete("/{id}")
def delete_activo(id: int):
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE activos SET is_deleted = TRUE, deleted_at = %s WHERE id = %s AND is_deleted = FALSE RETURNING id;", (datetime.utcnow(), id))
        borrado = cur.fetchone()
        conn.commit()
    conn.close()
    if not borrado:
        raise HTTPException(404, "Activo no encontrado")
    return {"message": "Borrado logico exitoso", "id": id}