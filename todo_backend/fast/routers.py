# todo_backend/fast/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database.db_session import get_db
from database.crud import UserRepository, TodoRepository
from security.pwd import hash_password
from fast.schemas import UserCreate, UserRead, TodoCreate, TodoRead, UserLogin
from model.models import User, Todo
user_router = APIRouter(prefix="/users", tags=["users"])
todo_router = APIRouter(prefix="/todos", tags=["todos"])


status_router = APIRouter()

@status_router.get("/status")
def status():
    return {"status": "running"}

@status_router.get("/status/db")
def status_db(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}

# ================= USERS ==================================================

@user_router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    """
    Example URL:
    http://127.0.0.1:8000/users/
    """
    repo = UserRepository(db)
    return repo.get_users()


@user_router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Example URL:
    http://127.0.0.1:8000/users/1
    """
    repo = UserRepository(db)
    user = repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/{user_id}/todos", response_model=list[TodoRead])
def get_todos_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Example URL:
    http://127.0.0.1:8000/users/2/todos
    """
    repo = TodoRepository(db)
    return repo.get_todos_by_user(user_id)


@user_router.get("/{user_id}/done_todos", response_model=list[TodoRead])
def get_done_todos(user_id: int, db: Session = Depends(get_db)):
    """
    Example URL:
    http://127.0.0.1:8000/users/1/done_todos
    """
    repo = UserRepository(db)
    return repo.get_done_todos(user_id)


@user_router.get("/{user_id}/open_todos", response_model=list[TodoRead])
def get_open_todos(user_id: int, db: Session = Depends(get_db)):
    """
    Example URL:
    http://127.0.0.1:8000/users/1/open_todos
    """
    repo = UserRepository(db)
    return repo.get_open_todos(user_id)

@user_router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    try:
        hashed_pw = hash_password(user.password)
        new_user = User(name=user.name, password=hashed_pw)
        return repo.create_user(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username existiert bereits")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB-Fehler: {e.__class__.__name__}")

@user_router.post("/authenticate", response_model=UserRead)
def authenticate_user(credentials: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.authenticate(credentials.name, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid name or password")
    return user
# ================= TODOS ==================================================

@todo_router.post("/", response_model=TodoRead)
def create_todo(todo: TodoCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Example URL:
    POST http://127.0.0.1:8000/todos/?user_id=1
    Request body:
    {
        "task": "Fenster putzen",
        "description": "Küche und Wohnzimmer",
        "deadline": "2025-11-05",
        "state": "OPEN"
    }
    """
    repo = TodoRepository(db)
    todo_db = Todo(**todo.model_dump(), user_id=user_id)
    return repo.create_todo(todo_db)


@todo_router.put("/{todo_id}/state", response_model=TodoRead)
def update_todo_state(todo_id: int, new_state: str, db: Session = Depends(get_db)):
    """
    Example URL:
    PUT http://127.0.0.1:8000/todos/1/state?new_state=DONE
    """
    repo = TodoRepository(db)
    todo = repo.update_todo_state(todo_id, new_state)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@todo_router.delete("/{todo_id}", response_model=bool)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    Example URL:
    DELETE http://127.0.0.1:8000/todos/1
    """
    repo = TodoRepository(db)
    return repo.delete_todo(todo_id)
