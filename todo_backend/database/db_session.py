# todo_backend/database/db_session.py
import os, ssl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")  # z.B. mysql+pymysql://avnadmin:PASS@host:port/defaultdb
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL fehlt")

# optional: PEM aus Env direkt als SSLContext (empfohlen)
ca_pem = os.getenv("AIVEN_CA_PEM")
ssl_arg = ssl.create_default_context(cadata=ca_pem) if ca_pem else None

engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": ssl_arg} if ssl_arg else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    """FastAPI-Dependency: gibt eine Session und schließt sie sauber."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
