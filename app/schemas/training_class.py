from datetime import time

from pydantic import BaseModel, ConfigDict


class TrainingClassCreate(BaseModel):
    name: str
    start_time: time
    end_time: time


class TrainingClassRead(BaseModel):
    id: int
    name: str
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)
