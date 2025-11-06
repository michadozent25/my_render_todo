# todo_backend/app/main.py
from fastapi import FastAPI
from fast.routers import user_router, todo_router
from database.db_session import Base, engine

app = FastAPI()
app.include_router(user_router)
app.include_router(todo_router)

# Tabellen anlegen (bei Bedarf)
Base.metadata.create_all(bind=engine)

# ---- Nur für LOKALE Entwicklung ----
if __name__ == "__main__":
    import uvicorn
    # Variante A: direkt mit dem App-Objekt (unkompliziert)
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    # Variante B (optional): über Modulpfad
    # uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
