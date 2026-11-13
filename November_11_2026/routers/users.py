import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(current_dir.parent) not in sys.path:
    sys.path.insert(1, str(current_dir.parent))

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import models
from schema import UserCreate, UserPublic

router = APIRouter()


# Create new users
@router.post("", response_model=UserPublic)
@router.post("/", response_model=UserPublic, include_in_schema=False)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Check whether the username already exists
    result = await db.execute(
        select(models.User).where(
           func.lower(models.User.username) == user.username.lower()
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    # Create new user
    new_user = models.User(
        username=user.username,
        password_hash= user.password
    )

    db.add(new_user)
    await db.commit()

    # Re-query user with todos eagerly loaded to ensure async serialization
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.todos))
        .where(models.User.id == new_user.id)
    )
    created_user = result.scalar_one()

    return created_user


# get users
@router.get("", response_model=list[UserPublic], status_code=status.HTTP_200_OK)
@router.get("/", response_model=list[UserPublic], status_code=status.HTTP_200_OK, include_in_schema=False)
async def get_user(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).options(selectinload(models.User.todos))
    )
    users = result.scalars().all()
    return users
