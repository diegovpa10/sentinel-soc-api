import os
from pydantic import BaseModel

class Settings(BaseModel):
    PG_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    PG_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    PG_USER: str = os.getenv("POSTGRES_USER", "soc_admin")
    PG_PASS: str = os.getenv("POSTGRES_PASSWORD", "soc_password123")
    PG_DB: str = os.getenv("POSTGRES_DB", "soc_relacional")

    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://soc_admin:soc_password123@localhost:27017/?authSource=admin")
    MONGO_DB: str = os.getenv("MONGO_DB_NAME", "soc_documental")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

settings = Settings()