from datetime import datetime

from pydantic import BaseModel, Field


class ScriptState(BaseModel):
    name: str
    cron: str
    running: bool


class CronUpdate(BaseModel):
    cron: str = Field(..., description="Cron-выражение, например */5 * * * *")


class LogOut(BaseModel):
    id: int
    script_name: str
    status: str
    output: str
    created_at: datetime

    class Config:
        from_attributes = True
