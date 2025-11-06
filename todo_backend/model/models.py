
from sqlalchemy import Column, Integer, String, Text, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database.db_session import Base
from model.enums import TodoState


class BaseRepr:
    """ generischhe __repr__Methode
        alle Klassen, die von  BaseRepr erben, bekommen automatisch eine
        def __repr__-Methode
    """
    def __repr__(self):
        fields = ", ".join(
            f"{col.name}={getattr(self, col.name)!r}"
            for col in self.__table__.columns
        )
        return f"<{self.__class__.__name__}({fields})>"

class Todo(Base, BaseRepr):
    __tablename__="todos"
    id=Column(Integer,primary_key=True)
    task=Column(String(100),nullable=False)
    description=Column(Text)
    deadline=Column(Date)
    state= Column(Enum(TodoState),nullable=False,default="OPEN")
    #  user_id,  evtl. user

    user_id=Column(Integer, ForeignKey("users.id"),nullable=False)
    user = relationship("User",back_populates="todos") # User-> Klasse

class User(Base,BaseRepr):
    __tablename__="users" 
    id=Column(Integer,primary_key=True)
    name=Column(String(100),nullable=False)
    password=Column(String(100),nullable=False) # FIXME Verschlüsselung
    todos = relationship("Todo",back_populates="user")