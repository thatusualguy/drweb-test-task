from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel


class TaskId(BaseModel):
    id: int


class StatusEnum(Enum):
    in_queue = "In Queue"
    run = "Run"
    completed = "Completed"


class TaskResponse(BaseModel):
    status: StatusEnum
    create_time: datetime
    start_time: datetime | None
    time_to_execute: timedelta | None

    class Config:
        use_enum_values = True
