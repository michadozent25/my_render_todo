from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.models import Todo, User
from security.pwd import verify_password

ALLOWED_STATES = {"OPEN", "DONE"}  # ggf. an dein Enum anpassen


class TodoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_todo(self, todo: Todo) -> Todo:
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    # optional, falls du es brauchst
    def find_all_todos(self) -> list[Todo]:
        return self.session.query(Todo).order_by(Todo.id.asc()).all()

    def new_todo_by_user(self, user_id: int, todo: Todo) -> Todo:
        user = self.session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        user.todos.append(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def get_todos_by_user(self, user_id: int) -> list[Todo]:
        return (
            self.session.query(Todo)
            .filter(Todo.user_id == user_id)
            .order_by(Todo.id.asc())
            .all()
        )

    def update_todo_state(self, todo_id: int, new_state: str) -> Optional[Todo]:
        if not new_state:
            return None
        state_norm = new_state.strip().upper()
        if state_norm not in ALLOWED_STATES:
            # optional: ValueError werfen und im Router 400 zurückgeben
            return None

        todo = self.session.get(Todo, todo_id)
        if not todo:
            return None

        todo.state = state_norm
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete_todo(self, todo_id: int) -> bool:
        todo = self.session.get(Todo, todo_id)
        if not todo:
            return False
        self.session.delete(todo)
        self.session.commit()
        return True


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_users(self) -> list[User]:
        return self.session.query(User).order_by(User.id.asc()).all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    # Für die Router-Endpunkte /users/{id}/done_todos und /open_todos
    def get_done_todos(self, user_id: int) -> list[Todo]:
        return (
            self.session.query(Todo)
            .filter(and_(Todo.user_id == user_id, Todo.state == "DONE"))
            .order_by(Todo.id.asc())
            .all()
        )

    def get_open_todos(self, user_id: int) -> list[Todo]:
        return (
            self.session.query(Todo)
            .filter(and_(Todo.user_id == user_id, Todo.state == "OPEN"))
            .order_by(Todo.id.asc())
            .all()
        )

    # Login bleibt wie gehabt
    def authenticate(self, name: str, password: str) -> User | None:
        user = self.session.query(User).filter(User.name == name).first()
        if user and verify_password(password, user.password):
            return user
        return None
