# todo_backend/database/db_session.py
import os, ssl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
DATABASE_URL = os.getenv("DATABASE_URL")  # z.B. mysql+pymysql://avnadmin:PASS@host:port/defaultdb
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL fehlt")

ca_pem = os.getenv("AIVEN_CA_PEM")  # kompletter PEM-Text (BEGIN/END inklusive)
ssl_arg = ssl.create_default_context(cadata=ca_pem) if ca_pem else None

print("HAS_AIVEN_CA_PEM:", bool(ca_pem), file=sys.stderr)
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": ssl_arg} if ssl_arg else {},  # <-- hier das SSLContext-Objekt
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
