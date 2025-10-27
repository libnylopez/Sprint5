import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _clean(s: str | None) -> str:
    return (s or "").strip().strip('"').strip("'")


class Settings:
    # Nuclia
    NUCLIA_API_BASE: str = _clean(os.getenv("NUCLIA_API_BASE"))
    KB: str = _clean(os.getenv("KB"))
    NUCLIA_TOKEN: str = _clean(os.getenv("NUCLIA_TOKEN"))

    # Anthropic
    ANTHROPIC_KEY: str = _clean(os.getenv("ANTHROPIC_KEY"))
    CLAUDE_MODEL: str = _clean(os.getenv("CLAUDE_MODEL") or "claude-sonnet-4-0")

    # Instrucciones del sistema
    INSTRUCTIONS: str = _clean(os.getenv("INSTRUCTIONS") or "Eres un asesor académico de la UVG Altiplano. Responde usando solo el contexto dado. Si no hay info suficiente, dilo.")


# Instancia global
settings = Settings()


