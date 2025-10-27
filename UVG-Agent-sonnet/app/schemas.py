from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ── Esquemas mejorados
class AskBody(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    size: Optional[int] = Field(default=30, ge=1, le=100)        # cuántos resultados pedir a Nuclia
    max_chunks: Optional[int] = Field(default=20, ge=1, le=50)   # cuántos párrafos meter al contexto
    use_semantic: Optional[bool] = Field(default=True)           # búsqueda semántica + keyword
    min_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)  # score mínimo


# ── Esquema para contexto conversacional del chatbot
class ConversationContext(BaseModel):
    author: str = Field(..., description="USER o NUCLIA")
    text: str = Field(..., description="Mensaje del usuario o respuesta de NUCLIA")


# ── Esquema para prompts personalizados
class CustomPrompt(BaseModel):
    system: Optional[str] = Field(None, description="System prompt para el comportamiento del modelo")
    user: Optional[str] = Field(None, description="User prompt con {context} y {question}")
    rephrase: Optional[str] = Field(None, description="Rephrase prompt para optimizar búsqueda")


# ── Esquema para el endpoint /nuclia-ask (usando el SDK de Nuclia)
class NucliaAskBody(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Pregunta del usuario")
    context: Optional[List[ConversationContext]] = Field(
        default=None, 
        description="Contexto conversacional para chatbot (historial de mensajes)"
    )
    rephrase: Optional[bool] = Field(
        default=False, 
        description="Si reprocesar la pregunta usando el contexto para mejorar búsqueda"
    )
    citations: Optional[str] = Field(
        default=None, 
        description="Formato de citaciones: 'default', 'llm_footnotes', o None"
    )
    filters: Optional[List[str]] = Field(
        default=None, 
        description="Filtros de búsqueda (ej: ['/classification.labels/tipo/documento'])"
    )
    prompt: Optional[CustomPrompt] = Field(
        default=None, 
        description="Prompts personalizados (system, user, rephrase)"
    )
    synchronous: Optional[bool] = Field(
        default=True, 
        description="Si devolver respuesta completa (True) o streaming (False)"
    )
    features: Optional[List[str]] = Field(
        default=None,
        description="Features de búsqueda: ['keyword', 'semantic', 'relations']"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=4096,
        description="Número máximo de tokens en la respuesta generada"
    )

