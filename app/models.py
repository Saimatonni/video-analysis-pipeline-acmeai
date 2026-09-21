from pydantic import BaseModel, Field

class Detection(BaseModel):
    frame_number: int = Field(ge=1)
    area: float = Field(gt=0)