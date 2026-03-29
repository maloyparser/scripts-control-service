import asyncio
import shutil
from datetime import datetime, timezone


async def main() -> None:
    await asyncio.sleep(0)
    total, used, free = shutil.disk_usage("/")
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] disk report")
    print(f"total_gb={total / (1024**3):.2f}")
    print(f"used_gb={used / (1024**3):.2f}")
    print(f"free_gb={free / (1024**3):.2f}")


if __name__ == "__main__":
    asyncio.run(main())
