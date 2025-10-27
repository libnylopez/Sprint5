from .clients import client
from .config import CLAUDE_MODEL

# ── Preproceso de consulta (igual que tu versión)
def preprocess_query(question: str) -> str:
    """Usa un LLM para refinar la pregunta conversacional en una consulta de búsqueda."""
    system_prompt = (
        "Eres un optimizador de consultas experto. Tu única tarea es tomar una pregunta "
        "conversacional o compleja y transformarla en una consulta de búsqueda concisa y "
        "llena de palabras clave. Devuelve SOLAMENTE la nueva consulta de búsqueda, sin "
        "explicaciones, frases introductorias o puntuación adicional. "
        "Ejemplo: '¿Cómo puedo restaurar una copia de seguridad?' -> 'restaurar copia seguridad'"
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=100,   # Una consulta corta es suficiente
        temperature=0.0,  # Queremos resultados consistentes, no creativos
        system=system_prompt,
        messages=[{"role": "user", "content": f"Pregunta original: {question}"}],
    )

    new_query = "".join(getattr(p, "text", "") for p in response.content).strip()
    print(new_query)

    if not new_query:
        return question
    return new_query
