# Todolist
## Version 0.1
## Model
* Todo
    * id
    * task:str
    * description:str
    * deadline:Date
    * state:(Enum("OPEN","IN_PROGRESS","DONE"))
    * optional: priority
* User
    * id
    * name
    * password


# Aufgabe
* Todolist soll um Schema und Routers ergenzt werden
* einige/wichte Funktionen sollen per Rest/FastAPI angeboten werden
* main soll automatisch uvicon starten
    ''' app = FastAPI()
        app.include_router(user_router)
        app.include_router(todo_router)
* database soll mit sqlite funktionieren todolist.db


