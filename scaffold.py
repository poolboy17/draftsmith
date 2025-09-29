from functools import lru_cache

from config import SCAFFOLD_MODEL
from llm import client


@lru_cache(maxsize=32)
def _scaffold_article_cached(prompt: str, links_key: tuple[str, ...], model: str) -> str:
    system_prompt = (
        "You are an article scaffold generator. Output a detailed outline with headings "
        "and bullets."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    if links_key:
        messages.append({"role": "user", "content": f"Links: {list(links_key)}"})
    return client.chat(model=model, messages=messages)


def scaffold_article(
    prompt: str, links: list[str] | None = None, model: str = SCAFFOLD_MODEL
) -> str:
    if not prompt or not str(prompt).strip():
        raise ValueError("Prompt must not be empty")
    links_key: tuple[str, ...] = tuple(links) if links else ()
    return _scaffold_article_cached(prompt, links_key, model)
