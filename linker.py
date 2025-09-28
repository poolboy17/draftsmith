import logging
import os

import requests

from config import MAX_LINKS, REQUEST_TIMEOUT, SERPAPI_KEY


def fetch_links(query: str, max_links: int = MAX_LINKS) -> list[str]:
    if os.getenv("DRY_RUN") == "1" or not SERPAPI_KEY:
        logging.info("DRY_RUN or missing SERPAPI_KEY; returning stub links")
        return [
            "https://example.com/article-1",
            "https://example.com/article-2",
            "https://example.com/article-3",
        ][:max_links]

    params = {"q": query, "api_key": SERPAPI_KEY, "num": max_links}
    resp = requests.get("https://serpapi.com/search", params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    results = resp.json().get("organic_results", [])
    links = [r.get("link") for r in results if r.get("link")]
    if not links:
        logging.warning(f"No links found for '{query}'")
    return links[:max_links]
