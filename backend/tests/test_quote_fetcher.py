import pytest
from scripts import quote_fetcher


@pytest.mark.asyncio
async def test_get_external_quote_success_from_first_source(monkeypatch) -> None:
    async def fake_fetch(session, url):
        return "A", f"content from {url}"

    monkeypatch.setattr(quote_fetcher, "fetch_quote", fake_fetch)

    author, content, source = await quote_fetcher.get_external_quote()
    assert author == "A"
    assert "content from" in content
    assert source == quote_fetcher.QUOTE_SOURCES[0]


@pytest.mark.asyncio
async def test_get_external_quote_fallback_message(monkeypatch) -> None:
    async def always_fail(session, url):
        raise RuntimeError("network down")

    monkeypatch.setattr(quote_fetcher, "fetch_quote", always_fail)

    author, content, source = await quote_fetcher.get_external_quote()
    assert author == "Unavailable"
    assert source == "none"
    assert "внешних" in content
