# todo_backend/app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from fast.routers import user_router, todo_router,status_router
from database.db_session import Base, engine, SessionLocal

app = FastAPI(title="Todo API")

# Router registrieren
app.include_router(user_router)
app.include_router(todo_router)
app.include_router(status_router)  # check backend

# ---- Lazy-Bootstrap statt beim Import blockieren ----
_bootstrapped = False

def _ensure_bootstrapped():
    """Tabellen nur einmal erzeugen – beim ersten Health-Aufruf."""
    global _bootstrapped
    if _bootstrapped:
        return
    Base.metadata.create_all(bind=engine)
    _bootstrapped = True

# ---- DB-Session Dependency (falls du sie hier brauchst) ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- Lokaler Dev-Start (Render startet über start.sh) ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
