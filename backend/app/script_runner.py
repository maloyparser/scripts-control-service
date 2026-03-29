import asyncio
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ScriptLog


async def run_script_and_log(script_name: str, script_path: Path, db_factory) -> None:
    """
    Запускает внешний python-скрипт, собирает stdout/stderr и пишет результат в БД.

    `db_factory` ожидается как фабрика async-сессий SQLAlchemy.
    """
    process = await asyncio.create_subprocess_exec(
        "python",
        str(script_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await process.communicate()
    output = stdout.decode("utf-8", errors="ignore").strip()
    status = "success" if process.returncode == 0 else "failed"

    async with db_factory() as session:
        session.add(
            ScriptLog(script_name=script_name, status=status, output=output or "(empty output)")
            )
        await session.commit()


async def get_logs(session: AsyncSession, script_name: str, limit: int = 50) -> list[ScriptLog]:
    """Возвращает последние логи скрипта в обратном хронологическом порядке."""
    query = (
        select(ScriptLog)
        .where(ScriptLog.script_name == script_name)
        .order_by(ScriptLog.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    return list(result.scalars().all())
