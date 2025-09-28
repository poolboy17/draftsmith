import argparse
import logging

import markdown
from dotenv import load_dotenv

from cache_util import cache_read, cache_write
from config import DEFAULT_CACHE_DIR
from config import MAX_LINKS as CFG_MAX_LINKS
from hydrate import hydrate_article
from linker import fetch_links
from output import write_output
from scaffold import scaffold_article
from version import __version__
from wordpress import publish_to_wordpress

load_dotenv()

logging.basicConfig(level=logging.INFO)


def clear_caches():
    from hydrate import hydrate_article as _hy

    # scaffold.scaffold_article delegates caching to _scaffold_article_cached
    from scaffold import _scaffold_article_cached as _sc

    _sc.cache_clear()
    _hy.cache_clear()
    logging.info("Cleared LRU caches")


def generate_article(args, prompt, links):
    cache_key_parts = [prompt, str(links), str(args.scaffold_model)]
    outline = None
    if not args.no_cache:
        outline = cache_read(args.cache_dir, "scaffold", cache_key_parts)
    if not outline:
        outline = scaffold_article(prompt, links, model=args.scaffold_model)
        if not args.no_cache:
            cache_write(args.cache_dir, "scaffold", cache_key_parts, outline)

    article = None
    hydrate_key = [outline, str(args.hydrate_model)]
    if not args.no_cache:
        article = cache_read(args.cache_dir, "hydrate", hydrate_key)
    if not article:
        article = hydrate_article(outline, model=args.hydrate_model)
        if not args.no_cache:
            cache_write(args.cache_dir, "hydrate", hydrate_key, article)
    if links:
        refs = "\n".join(f"- {link}" for link in links)
        article += "\n## References\n" + refs
    return article


def main() -> None:
    parser = argparse.ArgumentParser(description="Article Generator CLI")
    parser.add_argument(
        "--prompt",
        required=False,
        help="Article topic or headline",
    )
    parser.add_argument(
        "--links",
        nargs="*",
        help="Manual list of reference URLs",
    )
    parser.add_argument(
        "--fetch-links",
        action="store_true",
        help="Fetch top URLs via SerpAPI",
    )
    parser.add_argument(
        "--max-links",
        type=int,
        default=CFG_MAX_LINKS,
        help="Max number of links to fetch (with --fetch-links)",
    )
    parser.add_argument(
        "--output",
        default="article.md",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        choices=["md", "html"],
        default="md",
        help="Output format",
    )
    parser.add_argument("--scaffold-model", help="Override scaffold model")
    parser.add_argument("--hydrate-model", help="Override hydrate model")
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear outline/hydration caches",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish to WordPress",
    )
    parser.add_argument(
        "--check-wp",
        action="store_true",
        help="Verify WordPress credentials/connectivity and exit",
    )
    parser.add_argument(
        "--status",
        choices=["draft", "publish"],
        default="draft",
        help="Publish status when --publish is used",
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        type=int,
        help="WordPress category IDs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without calling external services (LLM/SerpAPI/WP)",
    )
    parser.add_argument(
        "--cache-dir",
        default=DEFAULT_CACHE_DIR,
        help="Directory for simple file cache",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable file cache for scaffold/hydrate",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"draftsmith {__version__}",
        help="Show version and exit",
    )
    args = parser.parse_args()

    # Fast path: connectivity check for WordPress
    if args.check_wp:
        import json

        from wordpress import check_wordpress_connection

        result = check_wordpress_connection()
        print(json.dumps(result, indent=2))
        if result.get("ok"):
            return
        raise SystemExit(1)

    if not args.prompt:
        parser.error("--prompt is required unless --check-wp is provided")

    if args.clear_cache:
        clear_caches()

    if args.dry_run:
        import os

        os.environ["DRY_RUN"] = "1"

    prompt = args.prompt
    links = args.links or (
        fetch_links(prompt, max_links=args.max_links) if args.fetch_links else None
    )

    article = generate_article(args, prompt, links)

    if args.publish:
        html = article if args.format == "html" else markdown.markdown(article)
        post = publish_to_wordpress(
            title=prompt,
            content_html=html,
            status=args.status,
            categories=args.categories,
        )
        print(f"Published to WordPress with ID {post.get('id')}")

    write_output(article, args.output, args.format)


if __name__ == "__main__":
    main()
