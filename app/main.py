from typing import Annotated, List, Optional
from fastapi import Depends, FastAPI, HTTPException
from app import settings
from sqlmodel import SQLModel, Field, create_engine, Session, select
from contextlib import asynccontextmanager

# Step 1: Creating Database Table Schema
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

# connection to the database
connection_string: str = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")

engine = create_engine(connection_string)

def create_db_tables():
    print("create_db_tables")
    SQLModel.metadata.create_all(engine)
    print("database table created successfully")

@asynccontextmanager
async def lifespan(todo_server: FastAPI):
    print("server startup check fastAPI from web")
    create_db_tables()
    yield

# Table data Get, Save

todo_server: FastAPI = FastAPI(lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session

@todo_server.get("/")
def hello():
    return {"Welcome to docker compose after rebuild"}

# GET method to fetch all todos
@todo_server.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        statement= select(Todo)
        todos = session.exec(statement).all()
        return todos

@todo_server.post("/todo")
def create_todo(Todo_data : Todo):
    with Session(engine) as session:
        session.add(Todo_data)
        session.commit()
        session.refresh(Todo_data)
        return Todo_data


# PUT method to update a todo
@todo_server.put("/todo/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_data: Todo):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        todo.title = todo_data.title
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

# PATCH method to partially update a todo
@todo_server.patch("/todo/{todo_id}", response_model=Todo)
def patch_todo(todo_id: int, todo_data: Todo):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        if todo_data.title:
            todo.title = todo_data.title
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

# DELETE method to delete a todo
@todo_server.delete("/todo/{todo_id}", response_model=Todo)
def delete_todo(todo_id: int):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        session.delete(todo)
        session.commit()
        return todo
