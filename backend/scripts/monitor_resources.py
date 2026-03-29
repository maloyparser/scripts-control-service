import asyncio
from datetime import datetime, timezone
import os

import aiohttp


async def check_domain(session: aiohttp.ClientSession, domain: str) -> str:
    try:
        async with session.get(domain, timeout=10) as response:
            return f"{domain} -> {response.status}"
    except Exception as exc:
        return f"{domain} -> ERROR: {exc}"


async def main() -> None:
    domains = os.getenv(
        "MONITOR_DOMAINS",
        "https://example.com,https://python.org,https://github.com",
    ).split(",")
    timestamp = datetime.now(timezone.utc).isoformat()
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[check_domain(session, d.strip()) for d in domains])
    print(f"[{timestamp}] monitor report")
    for line in results:
        print(line)


if __name__ == "__main__":
    asyncio.run(main())
