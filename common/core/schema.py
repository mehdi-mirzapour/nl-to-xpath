from abc import ABC
from pydantic import BaseModel
from typing import Optional, Any

class RequestSchema(ABC, BaseModel):
    pass


class ResponseSchema(BaseModel):
    status: int
    message: str
    data: Any
    duration: float

class TokenUsage(BaseModel):
    input_token: int
    model_name: str
    output_token: int
    image_token: Optional[int] = None
    quality: Optional[str] = None

