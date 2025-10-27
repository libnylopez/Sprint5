from app.settings import settings

# ── Config (idéntica a tu script)
NUCLIA_API_BASE = settings.NUCLIA_API_BASE
KB = settings.KB
NUCLIA_TOKEN = settings.NUCLIA_TOKEN
HEADERS = {"x-api-key": NUCLIA_TOKEN.strip()}

ANTHROPIC_KEY = settings.ANTHROPIC_KEY
CLAUDE_MODEL = settings.CLAUDE_MODEL
INSTRUCTIONS = settings.INSTRUCTIONS
