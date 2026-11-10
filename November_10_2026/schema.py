from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=5)


class UserCreate(UserBase):
    pass


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    todos: list["TodoPublic"] = Field(default_factory=list)


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1, max_length=150)


class TodoCreate(TodoBase):
    pass


class TodoPublic(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str