from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base
from app.models import ScriptLog
from app.script_runner import get_logs


@pytest.mark.asyncio
async def test_get_logs_returns_latest_first() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    now = datetime.utcnow()
    async with session_factory() as session:
        session.add_all(
            [
                ScriptLog(script_name="monitor_resources", status="success", output="old", created_at=now),
                ScriptLog(
                    script_name="monitor_resources",
                    status="success",
                    output="new",
                    created_at=now + timedelta(seconds=5),
                ),
            ]
        )
        await session.commit()

    async with session_factory() as session:
        logs = await get_logs(session, "monitor_resources", limit=10)

    assert len(logs) == 2
    assert logs[0].output == "new"
    assert logs[1].output == "old"
