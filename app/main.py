from fastapi import FastAPI
from app.core.database import init_postgres
from app.routers import activos, incidentes

app = FastAPI(
    title="SentinelSOC Multi-Database API",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    init_postgres()

app.include_router(activos.router)
app.include_router(incidentes.router)