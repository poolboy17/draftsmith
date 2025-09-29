from functools import lru_cache

from config import HYDRATE_MODEL
from llm import client


@lru_cache(maxsize=32)
def hydrate_article(outline: str, model: str = HYDRATE_MODEL) -> str:
    if not outline or not str(outline).strip():
        raise ValueError("Outline must not be empty")
    system_prompt = (
        "You are a writing assistant. Transform the outline into a full article with "
        "context, examples, transitions."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": outline},
    ]
    return client.chat(model=model, messages=messages)
