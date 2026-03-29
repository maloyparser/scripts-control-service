import asyncio
from datetime import datetime, timezone

import aiohttp

QUOTE_SOURCES = [
    "https://api.github.com/zen",
]


async def fetch_quote(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    async with session.get(url, timeout=10) as response:
        response.raise_for_status()
        text = (await response.text()).strip()
        return "GitHub Zen", text


async def get_external_quote() -> tuple[str, str, str]:
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for url in QUOTE_SOURCES:
            try:
                author, content = await fetch_quote(session, url)
                if content:
                    return author, content, url
            except Exception:
                continue

    return "Unavailable", "Не удалось получить цитату из внешних источников", "none"


async def main() -> None:
    author, content, source = await get_external_quote()
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] quote fetched")
    print(f"source={source}")
    print(f"author={author}")
    print(content)
    await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
