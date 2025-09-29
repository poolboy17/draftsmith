import os

from dotenv import load_dotenv

# Ensure .env is loaded as early as possible so downstream imports see env vars
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SCAFFOLD_MODEL = "x-ai/grok-4-fast:free"
HYDRATE_MODEL = "openai/gpt-5"
MAX_LINKS = 5
REQUEST_TIMEOUT = 10
USER_AGENT = os.getenv("USER_AGENT", "draftsmith")
MAX_MEDIA_BYTES = int(os.getenv("MAX_MEDIA_BYTES", str(10 * 1024 * 1024)))  # 10MB default
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")
DEFAULT_CACHE_DIR = ".cache"
