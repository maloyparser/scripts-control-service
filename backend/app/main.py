from contextlib import asynccontextmanager
import json
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Base, engine, get_db
from .schemas import CronUpdate, LogOut, ScriptState
from .scheduler import script_scheduler
from .script_runner import get_logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    script_scheduler.start()
    yield
    script_scheduler.shutdown()


app = FastAPI(title="Scripts Control Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_script(script_name: str) -> None:
    if script_name not in script_scheduler.scripts:
        raise HTTPException(status_code=404, detail="Script not found")

@app.get("/")
async def root() -> dict:
    return {
        "service": "Scripts Control Service",
        "status": "ok",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}

@app.get("/api/scripts", response_model=list[ScriptState])
async def list_scripts(line_by_line: bool = False):
    states = [ScriptState(**item) for item in script_scheduler.list_states()]
    if line_by_line:
        payload = "\n".join(json.dumps(state.model_dump(), ensure_ascii=False) for state in states)
        return PlainTextResponse(content=payload, media_type="application/x-ndjson")
    return states


@app.put("/api/scripts/{script_name}/cron", response_model=ScriptState)
async def update_cron(script_name: str, payload: CronUpdate) -> ScriptState:
    ensure_script(script_name)
    try:
        state = script_scheduler.set_cron(script_name, payload.cron)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ScriptState(**state)


@app.post("/api/scripts/{script_name}/start", response_model=ScriptState)
async def start_script(script_name: str) -> ScriptState:
    ensure_script(script_name)
    return ScriptState(**script_scheduler.set_running(script_name, True))


@app.post("/api/scripts/{script_name}/pause", response_model=ScriptState)
async def pause_script(script_name: str) -> ScriptState:
    ensure_script(script_name)
    return ScriptState(**script_scheduler.set_running(script_name, False))


@app.get("/api/scripts/{script_name}/logs", response_model=list[LogOut])
async def script_logs(
    script_name: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[LogOut]:
    ensure_script(script_name)
    rows = await get_logs(db, script_name, limit=min(limit, 200))
    return [LogOut.model_validate(row) for row in rows]
