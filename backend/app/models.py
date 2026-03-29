from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class ScriptLog(Base):
    __tablename__ = "script_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    script_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(32))
    output: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
