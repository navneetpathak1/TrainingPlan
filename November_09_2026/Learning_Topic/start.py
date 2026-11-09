import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(min_length= 1, max_length = 30)
    content: str = Field(min_length= 1, max_length = 120)

class CreateTodo(TodoBase):
    pass

class ReturnTodo(TodoBase):
    id: int

class UpdateTodo(BaseModel):
    title: str | None = Field(default=None, min_length= 1, max_length = 30)
    content: str | None = Field(default=None, min_length= 1, max_length = 120)

app = FastAPI()

todos = [
    {
        "id": 1,
        "title": "hello",
        "content": "world"
    },
    {
        "id": 2,
        "title": "hello",
        "content": "world"
    }
]

# get all todos
@app.get("/", response_model=list[ReturnTodo])
def return_Todo():
    return todos

# get todo with todo id
@app.get("/todo/{todo_id}", response_model=ReturnTodo)
def return_todo_with_id(todo_id:int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with todo_id: {todo_id} not found")


# create todo

@app.post("/createTodo", response_model=ReturnTodo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: CreateTodo):
    n = len(todos)
    new_id = todos[n-1]["id"] + 1
    newTodo = {
        "id": new_id,
        "title": todo.title,
        "content": todo.content
    }

    todos.append(newTodo)

    return newTodo

# update 

@app.put("/update/{todo_id}", response_model=ReturnTodo, status_code=status.HTTP_200_OK)
def update_todo(todo_id:int, data:CreateTodo):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["title"] = data.title
            todo["content"] = data.content

            return todo

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not exist")


@app.patch("/update/{todo_id}", response_model=ReturnTodo, status_code=status.HTTP_200_OK)
def update_todo(todo_id:int, data:UpdateTodo):
    update_data = data.model_dump(exclude_unset=True)
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(update_data)

            return todo

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not exist")


@app.delete("/delete/{todo_id}", status_code=status.HTTP_200_OK)
def delete(todo_id:int):
    for todo in todos:
        if todo["id"] == todo_id:
            todos.remove(todo)
            return "Todo is deleted"

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not exist")
    