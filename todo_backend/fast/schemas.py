# schemas.py
from pydantic import BaseModel,Field,ConfigDict
from datetime import date
from model.enums import TodoState

class TodoBase(BaseModel):
    task: str
    description: str | None = None
    deadline: date | None = None
    state: TodoState = TodoState.OPEN

class TodoCreate(TodoBase):
    pass

class TodoRead(TodoBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True) # NEU!!!
#----------------------- User ------------------------------------------
class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)

class UserRead(UserBase):
    id: int
    todos: list[TodoRead] = []

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True) # NEU!!!

class UserLogin(UserBase):
    password: str