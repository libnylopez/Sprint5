from anthropic import Anthropic
from .config import ANTHROPIC_KEY

# ── Cliente Anthropic
client = Anthropic(api_key=ANTHROPIC_KEY)
