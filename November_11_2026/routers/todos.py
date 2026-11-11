import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(current_dir.parent) not in sys.path:
    sys.path.insert(1, str(current_dir.parent))

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
import models
from schema import TodoCreate, TodoPublic

router = APIRouter()


# all todos
@router.get("", name="todos", response_model=list[TodoPublic], status_code=status.HTTP_200_OK)
@router.get("/", response_model=list[TodoPublic], status_code=status.HTTP_200_OK, include_in_schema=False)
async def home(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Todos))
    todos = result.scalars().all()

    if not todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todo found")
    return todos


# create new todos
@router.post("/{user_id}", response_model=TodoPublic)
async def create_todo(user_id: int, todo: TodoCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    userExist = user.scalar_one_or_none()

    if not userExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    newTodo = models.Todos(
        title=todo.title,
        content=todo.content,
        user_id=user_id
    )

    db.add(newTodo)
    await db.commit()
    await db.refresh(newTodo)

    return newTodo


#  Update todo
@router.put("/{user_id}/{todo_id}", response_model=TodoPublic)
async def update_todo(user_id: int, todo_id: int, todo: TodoCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    ans = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    result = ans.scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    todo_ans = await db.execute(
        select(models.Todos).where(
            (models.Todos.id == todo_id) & (models.Todos.user_id == user_id)
        )
    )

    todo_result = todo_ans.scalar_one_or_none()

    if not todo_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    todo_result.title = todo.title
    todo_result.content = todo.content

    await db.commit()
    await db.refresh(todo_result)

    return todo_result


# delete todo
@router.delete("/{user_id}/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user_id: int, todo_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    ans = await db.execute(
        select(models.Todos).where(
            (models.Todos.id == todo_id) & (models.Todos.user_id == user_id)
        )
    )

    result = ans.scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    await db.delete(result)
    await db.commit()

    return None


# transaction
@router.post("/transaction/{user_id}", response_model=TodoPublic)
async def create_todo_withTransaction(user_id: int, todo: TodoCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        user = await db.execute(
            select(models.User).where(models.User.id == user_id)
        )

        userExist = user.scalar_one_or_none()
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
        await db.commit()
        await db.refresh(newTodo)

        return newTodo

    except Exception:
        await db.rollback()
        raise
