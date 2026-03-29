import pytest
from app.scheduler import ScriptScheduler


@pytest.mark.parametrize(
    "cron_expr",
    ["*/1 * * * *", "0 */2 * * 1-5", "15 3 1 * *"],
)
def test_parse_valid_cron(cron_expr: str) -> None:
    scheduler = ScriptScheduler()
    trigger = scheduler._parse_cron(cron_expr)
    assert trigger is not None


def test_parse_invalid_cron() -> None:
    scheduler = ScriptScheduler()
    with pytest.raises(ValueError):
        scheduler._parse_cron("*/5 * *")


def test_cron_aliases_are_supported() -> None:
    scheduler = ScriptScheduler()
    hourly_state = scheduler.set_cron("monitor_resources", "hourly")
    assert hourly_state["cron"] == "0 * * * *"
