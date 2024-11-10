from pydantic import BaseModel

class BbSearchInput(BaseModel):
    query: str
    count: int = 10
