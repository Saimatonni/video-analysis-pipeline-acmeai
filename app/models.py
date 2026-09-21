from typing import Literal
from pydantic import BaseModel, Field

class Detection(BaseModel):
    frame_number: int = Field(ge=1)
    area: float = Field(gt=0)


class ProgressReport(BaseModel):
    run_id: str
    status: Literal[
        "started",
        "running",
        "completed",
        "failed",
    ]

    frames_seen: int = Field(ge=0)
    frames_analyzed: int = Field(ge=0)
    valid_detections: int = Field(ge=0)
    invalid_detections: int = Field(ge=0)

    progress_percent: float = Field(
        ge=0,
        le=100,
    )


class JobEvent(BaseModel):
    run_id: str

    event: Literal[
        "started",
        "completed",
        "failed",
        "reporting_failed",
    ]

    message: str    