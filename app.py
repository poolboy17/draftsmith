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
from wordpress import check_wordpress_connection

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="Draftsmith Web")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
TEMPLATE_RESULT = "result.html"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, prompt: str = Form(...), fetch_links_flag: bool = Form(False)):
    try:
        if not prompt or not str(prompt).strip():
            return templates.TemplateResponse(
                request,
                TEMPLATE_RESULT,
                {"prompt": "", "outline": "", "article_html": "", "error": "Prompt is required."},
            )
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
            request,
            TEMPLATE_RESULT,
            {
                "prompt": prompt,
                "outline": outline,
                "article_html": article_html,
                "error": None,
            },
        )
    except Exception as exc:  # noqa: BLE001
        # Minimal error page
        return templates.TemplateResponse(
            request,
            TEMPLATE_RESULT,
            {
                "prompt": prompt,
                "outline": "",
                "article_html": "",
                "error": str(exc),
            },
        )


# Optional: simple health check
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/wp")
async def health_wp():
    # Returns a minimal summary of WP connectivity (safe GET only)
    result = check_wordpress_connection()
    # Do not echo secrets; include only safe fields
    user = result.get("user")
    user_id = user.get("id") if isinstance(user, dict) else None
    user_name = user.get("name") if isinstance(user, dict) else None
    return {
        "ok": result.get("ok"),
        "status_code": result.get("status_code"),
        "url": result.get("url"),
        "user": {"id": user_id, "name": user_name},
        "error": result.get("error") if not result.get("ok") else None,
    }
