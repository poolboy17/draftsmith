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
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")
DEFAULT_CACHE_DIR = ".cache"
