from functools import lru_cache

from config import SCAFFOLD_MODEL
from llm import client


@lru_cache(maxsize=32)
def scaffold_article(
    prompt: str, links: list[str] | None = None, model: str = SCAFFOLD_MODEL
) -> str:
    system_prompt = (
        "You are an article scaffold generator. Output a detailed outline with headings "
        "and bullets."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    if links:
        messages.append({"role": "user", "content": f"Links: {links}"})
    return client.chat(model=model, messages=messages)
