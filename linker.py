import logging
import os

import requests

from config import MAX_LINKS, REQUEST_TIMEOUT, SERPAPI_KEY, USER_AGENT


def fetch_links(query: str, max_links: int = MAX_LINKS) -> list[str]:
    if not query or not str(query).strip():
        return []
    # clamp max_links
    try:
        max_links = max(1, min(int(max_links), MAX_LINKS))
    except Exception:  # noqa: BLE001
        max_links = MAX_LINKS
    if os.getenv("DRY_RUN") == "1" or not SERPAPI_KEY:
        logging.info("DRY_RUN or missing SERPAPI_KEY; returning stub links")
        return [
            "https://example.com/article-1",
            "https://example.com/article-2",
            "https://example.com/article-3",
        ][:max_links]

    params = {"q": query, "api_key": SERPAPI_KEY, "num": max_links}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        logging.warning(f"SerpAPI request failed: {exc}")
        return []

    results = payload.get("organic_results", []) if isinstance(payload, dict) else []
    links = [r.get("link") for r in results if r.get("link")]
    if not links:
        logging.warning(f"No links found for '{query}'")
    return links[:max_links]
