import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, status, Depends
from schema import TodoCreate, TodoPublic, UserPublic, UserSummary, UserCreate
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
app = FastAPI()

import models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)


# all todos
@app.get("/", name="home")
@app.get("/todos", name= "todos", response_model= list[TodoPublic], status_code=status.HTTP_200_OK)
def home(db: Annotated[Session, Depends(get_db)]):

    result = db.execute(select(models.Todos))

    todos = result.scalars().all()

    if not todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todo found")
    return todos



@app.get("/users", status_code=status.HTTP_200_OK)
def get_user(db: Annotated[Session, Depends(get_db)]):

    result = db.execute(select(models.User))
    users = result.scalars().all()
    return users



# create new users

@app.post("/create/user", response_model=UserPublic)
def create_user(user: UserCreate,  db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.username == user.username),
    ).scalar_one_or_none()

    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist"
        )
    
    new_user = models.User(
        username= user.username,
        password= user.password
    )
    

    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return new_user


# create new todos

@app.post("/create/{user_id}", response_model=TodoPublic)
def create_todo(user_id: int, todo: TodoCreate, db: Annotated[Session, Depends(get_db)]):
    userExist = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalar_one_or_none()

    if not userExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    newTodo = models.Todos(
        title=todo.title,
        content=todo.content,
        user_id=user_id
    )

    db.add(newTodo)
    db.commit()
    db.refresh(newTodo)

    return newTodo

#  Update todo
@app.put("/update/{user_id}/{todo_id}", response_model=TodoPublic)
def update_todo(user_id: int, todo_id: int, todo: TodoCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id)).scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    todo_result = db.execute(select(models.Todos).where((models.Todos.id == todo_id)&(models.Todos.user_id == user_id))).scalar_one_or_none()

    if not todo_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    todo_result.title = todo.title
    todo_result.content = todo.content

    db.commit()
    db.refresh(todo_result)

    return todo_result


# delete todo

@app.delete("/delete/{user_id}/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user_id: int, todo_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Todos).where(
            (models.Todos.id == todo_id) &
            (models.Todos.user_id == user_id)
        )
    ).scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    db.delete(result)
    db.commit()

    return None

# transaction

@app.post("/todo/{user_id}", response_model=TodoPublic)
def create_todo_withTransaction(user_id: int, todo: TodoCreate, db: Annotated[Session, Depends(get_db)]):
    try:
        userExist = db.execute(
            select(models.User).where(models.User.id == user_id)
        ).scalar_one_or_none()

        if not userExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        newTodo = models.Todos(
            title=todo.title,
            content=todo.content,
            user_id=user_id
        )

        db.add(newTodo)
        db.commit()
        db.refresh(newTodo)

        return newTodo

    except Exception:
        db.rollback()
        raise