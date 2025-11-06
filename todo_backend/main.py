from fastapi import FastAPI
from fast.routers import user_router, todo_router
from database.db_session import Base, engine

app = FastAPI()
app.include_router(user_router)
app.include_router(todo_router)

Base.metadata.create_all(bind=engine)


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)