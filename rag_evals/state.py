
from pydantic import BaseModel, Field

class State(BaseModel):
    query: str
    answer: str = ""
    citations: list[str] = Field(default_factory=list)
