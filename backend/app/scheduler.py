from dataclasses import dataclass
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import settings
from .db import SessionLocal
from .script_runner import run_script_and_log

CRON_ALIASES = {
    "minutely": "*/1 * * * *",
    "hourly": "0 * * * *",
    "daily": "0 0 * * *",
    "weekly": "0 0 * * 0",
}

@dataclass
class ScriptConfig:
    name: str
    filename: str
    cron: str
    running: bool = True


class ScriptScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scripts: dict[str, ScriptConfig] = {
            "monitor_resources": ScriptConfig("monitor_resources", "monitor_resources.py", "*/1 * * * *", True),
            "disk_report": ScriptConfig("disk_report", "disk_report.py", "*/2 * * * *", True),
            "quote_fetcher": ScriptConfig("quote_fetcher", "quote_fetcher.py", "*/3 * * * *", True),
        }

    def start(self) -> None:
        self._sync_jobs()
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def _script_path(self, cfg: ScriptConfig) -> Path:
        return Path(settings.scripts_dir) / cfg.filename

    @staticmethod
    def _normalize_cron(cron_expr: str) -> str:
        expr = cron_expr.strip().lower()
        return CRON_ALIASES.get(expr, cron_expr.strip())

    @staticmethod
    def _parse_cron(cron_expr: str) -> CronTrigger:
        fields = cron_expr.split()
        if len(fields) != 5:
            raise ValueError(
                "Неверный cron. Используйте формат '*/5 * * * *' или алиасы: minutely/hourly/daily/weekly"
            )
        minute, hour, day, month, day_of_week = fields
        return CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
        )

    def _sync_jobs(self) -> None:
        for cfg in self.scripts.values():
            if self.scheduler.get_job(cfg.name):
                self.scheduler.remove_job(cfg.name)
            if cfg.running:
                self.scheduler.add_job(
                    run_script_and_log,
                    self._parse_cron(cfg.cron),
                    id=cfg.name,
                    kwargs={
                        "script_name": cfg.name,
                        "script_path": self._script_path(cfg),
                        "db_factory": SessionLocal,
                    },
                    replace_existing=True,
                )

    def list_states(self) -> list[dict]:
        return [
            {"name": cfg.name, "cron": cfg.cron, "running": cfg.running}
            for cfg in self.scripts.values()
        ]

    def set_cron(self, name: str, cron: str) -> dict:
        cfg = self.scripts[name]
        normalized_cron = self._normalize_cron(cron)
        self._parse_cron(normalized_cron)
        cfg.cron = normalized_cron
        self._sync_jobs()
        return {"name": cfg.name, "cron": cfg.cron, "running": cfg.running}

    def set_running(self, name: str, running: bool) -> dict:
        cfg = self.scripts[name]
        cfg.running = running
        self._sync_jobs()
        return {"name": cfg.name, "cron": cfg.cron, "running": cfg.running}


script_scheduler = ScriptScheduler()
