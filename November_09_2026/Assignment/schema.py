from pydantic import BaseModel, Field, ConfigDict

class TodoBase(BaseModel):
    title: str = Field(min_length= 1, max_length = 30)
    content: str = Field(min_length= 1, max_length = 120)

class CreateTodo(TodoBase):
    pass

class ReturnTodo(TodoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class UpdateTodo(BaseModel):
    title: str | None = Field(default=None, min_length= 1, max_length = 30)
    content: str | None = Field(default=None, min_length= 1, max_length = 120)
