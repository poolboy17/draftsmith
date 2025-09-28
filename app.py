from __future__ import annotations

import markdown as md
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from config import MAX_LINKS
from hydrate import hydrate_article
from linker import fetch_links
from scaffold import scaffold_article

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="Draftsmith Web")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, prompt: str = Form(...), fetch_links_flag: bool = Form(False)):
    try:
        links = fetch_links(prompt, max_links=MAX_LINKS) if fetch_links_flag else None

        # Build outline and article; leverage existing modules (no file cache here for simplicity)
        outline = scaffold_article(prompt, links=links)
        article_md = hydrate_article(outline)
        if links:
            refs = "\n".join(f"- {link}" for link in links)
            article_md += "\n## References\n" + refs

        # Render Markdown to HTML for display
        article_html = md.markdown(article_md)

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "prompt": prompt,
                "outline": outline,
                "article_html": article_html,
            },
        )
    except Exception as exc:  # noqa: BLE001
        # Minimal error page
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "prompt": prompt,
                "outline": "",
                "article_html": f"<p>Error: {str(exc)}</p>",
            },
        )


# Optional: simple health check
@app.get("/health")
async def health():
    return {"status": "ok"}
