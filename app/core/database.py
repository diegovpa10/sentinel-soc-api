import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
import redis
from app.core.config import settings

def get_pg_connection():
    return psycopg2.connect(
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        user=settings.PG_USER,
        password=settings.PG_PASS,
        dbname=settings.PG_DB,
        cursor_factory=RealDictCursor
    )

def init_postgres():
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS activos (
                id SERIAL PRIMARY KEY,
                hostname VARCHAR(100) UNIQUE NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                criticidad VARCHAR(20) DEFAULT 'media',
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS incidentes (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(150) NOT NULL,
                severidad VARCHAR(20) NOT NULL,
                estado VARCHAR(30) DEFAULT 'abierto',
                activo_id INT NOT NULL REFERENCES activos(id),
                analista VARCHAR(100) NOT NULL,
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP NULL
            );
        """)
        conn.commit()
    conn.close()

mongo_client = MongoClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB]

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)