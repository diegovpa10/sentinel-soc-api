from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.core.database import get_pg_connection

router = APIRouter(prefix="/incidentes", tags=["PostgreSQL - Incidentes"])

class IncidenteCreate(BaseModel):
    titulo: str
    severidad: str
    activo_id: int
    analista: str

class IncidentePatch(BaseModel):
    estado: Optional[str] = None

@router.get("", response_model=List[dict])
def get_incidentes():
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM incidentes WHERE is_deleted = FALSE;")
        datos = cur.fetchall()
    conn.close()
    return datos

@router.post("", status_code=status.HTTP_201_CREATED)
def create_incidente(payload: IncidenteCreate):
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO incidentes (titulo, severidad, activo_id, analista)
            VALUES (%s, %s, %s, %s) RETURNING *;
        """, (payload.titulo, payload.severidad, payload.activo_id, payload.analista))
        nuevo = cur.fetchone()
        conn.commit()
    conn.close()
    return nuevo

@router.patch("/{id}")
def patch_incidente(id: int, payload: IncidentePatch):
    if not payload.estado:
        raise HTTPException(status_code=400, detail="Sin campos a modificar")
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE incidentes SET estado = %s WHERE id = %s AND is_deleted = FALSE RETURNING *;", (payload.estado, id))
        actualizado = cur.fetchone()
        conn.commit()
    conn.close()
    if not actualizado:
        raise HTTPException(404, "Incidente no encontrado")
    return actualizado

@router.delete("/{id}")
def delete_incidente(id: int):
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE incidentes SET is_deleted = TRUE, deleted_at = %s WHERE id = %s AND is_deleted = FALSE RETURNING id;", (datetime.utcnow(), id))
        borrado = cur.fetchone()
        conn.commit()
    conn.close()
    if not borrado:
        raise HTTPException(404, "Incidente no encontrado")
    return {"message": "Borrado logico exitoso", "id": id}