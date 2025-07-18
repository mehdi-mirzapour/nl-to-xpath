from typing import List, Optional
from pydantic import BaseModel
from common.core.schema import RequestSchema, ResponseSchema

class ImageRequest(RequestSchema):
    image: str
    
class ImageResponse(BaseModel):
    image: str
