import requests
from nuclia import sdk
from .config import NUCLIA_API_BASE, KB, HEADERS, NUCLIA_TOKEN
from typing import Optional, List, Dict, Any
import base64


# ── Inicializar SDK de Nuclia (se hace una vez al importar el módulo)
def _init_nuclia_sdk():
    """Inicializa el SDK de Nuclia con la API key y URL."""
    try:
        # Configurar el SDK con la URL y API key
        # El SDK necesita: url, kbid, api_key
        sdk.NucliaAuth().url(NUCLIA_API_BASE).api_key(NUCLIA_TOKEN).kb(KB)
        return True
    except Exception as e:
        print(f"Warning: No se pudo inicializar SDK de Nuclia: {e}")
        return False

# Inicializar al importar
_SDK_INITIALIZED = _init_nuclia_sdk()

# ── Búsqueda Nuclia mejorada
def nuclia_search(
    query: str, 
    size: int = 20,
    features: Optional[List[str]] = None,
    filters: Optional[List[str]] = None,
    faceted: Optional[List[str]] = None,
    sort: Optional[str] = None,
    min_score: Optional[float] = None,
    vectorset: str = "multilingual-2024-05-06"
) -> dict:
    """
    Búsqueda mejorada en Nuclia con múltiples opciones.
    
    Args:
        query: Texto a buscar
        size: Número de resultados (default: 20)
        features: Tipos de búsqueda ['keyword', 'semantic', 'relations']
        filters: Filtros como ['/classification.labels/tipo/documento']
        faceted: Campos para facetado ['/classification.labels']
        sort: Ordenamiento ('created', 'modified', 'score')
        min_score: Score mínimo para resultados (0.0-1.0)
        vectorset: Conjunto de vectores para búsqueda semántica
    """
    url = f"{NUCLIA_API_BASE}/kb/{KB}/search"
    
    # Parámetros base
    params: Dict[str, Any] = {
        "query": query,
        "size": size,
    }
    
    # Búsqueda híbrida por defecto (keyword + semantic)
    if features is None:
        features = ["keyword", "semantic"]
    params["features"] = features
    
    # Vectorset para búsqueda semántica
    if "semantic" in features:
        params["vectorset"] = vectorset
    
    # Filtros opcionales
    if filters:
        params["filters"] = filters
    
    # Facetado
    if faceted:
        params["faceted"] = faceted
    
    # Ordenamiento
    if sort:
        params["sort"] = sort
    
    # Score mínimo
    if min_score is not None:
        params["min_score"] = min_score
    
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


# ── Obtener recurso específico de Nuclia usando SDK
def get_nuclia_resource(resource_id: str) -> dict:
    """
    Obtiene información completa de un recurso específico de Nuclia usando el SDK.
    
    Args:
        resource_id: ID del recurso
        
    Returns:
        dict con información del recurso incluyendo archivos disponibles
    """
    try:
        # Usar SDK de Nuclia
        resource = sdk.NucliaResource()
        data = resource.get(rid=resource_id, show=["basic", "values", "origin"])
        return data
    except Exception as e:
        print(f"Error obteniendo recurso {resource_id} con SDK: {e}")
        # Fallback a requests si el SDK falla
        url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{resource_id}"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()


# ── Obtener URL temporal de descarga de archivo usando SDK
def get_temporal_download_url(resource_id: str, file_id: str, ttl: int = 3600) -> str:
    """
    Obtiene una URL temporal de descarga para un archivo usando el SDK de Nuclia.
    Esta URL incluye un token temporal y no requiere autenticación adicional.
    
    Args:
        resource_id: ID del recurso
        file_id: ID del campo del archivo
        ttl: Tiempo de vida en segundos (default: 3600 = 1 hora)
        
    Returns:
        str con la URL temporal de descarga
    """
    try:
        # Usar SDK de Nuclia para obtener URL temporal
        resource = sdk.NucliaResource()
        url = resource.temporal_download_url(rid=resource_id, file_id=file_id, ttl=ttl)
        return url
    except Exception as e:
        print(f"Error obteniendo URL temporal para {resource_id}/{file_id}: {e}")
        # Si falla, construir URL estándar (requiere autenticación)
        return f"{NUCLIA_API_BASE}/kb/{KB}/resource/{resource_id}/file/{file_id}/download"


# ── Obtener archivo de recurso
def get_resource_file(resource_id: str, field_id: str = "file") -> dict:
    """
    Obtiene la información de descarga de un archivo de un recurso.
    
    Args:
        resource_id: ID del recurso
        field_id: ID del campo del archivo (default: "file")
        
    Returns:
        dict con URL de descarga y metadata del archivo
    """
    url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{resource_id}/{field_id}/download"
    
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    
    # La respuesta puede ser JSON con URL o puede ser el archivo directamente
    content_type = r.headers.get("content-type", "")
    
    if "application/json" in content_type:
        return r.json()
    else:
        # Si es el archivo directamente, devolverlo como base64
        return {
            "content": base64.b64encode(r.content).decode('utf-8'),
            "content_type": content_type,
            "size": len(r.content)
        }


# ── Descargar archivo de recurso (proxy para no exponer API key)
def download_resource_file(resource_id: str, file_id: str):
    """
    Descarga un archivo de un recurso de Nuclia usando el SDK.
    Según la documentación, debes usar download_file() del SDK, no construir URLs manualmente.
    
    Args:
        resource_id: ID del recurso
        file_id: ID del file field (ej: "15323a97500211296cae8abeb5daec6e")
        
    Returns:
        bytes con el contenido del archivo y metadata
    """
    try:
        # Usar SDK de Nuclia para descargar
        import tempfile
        import os
        
        resource = sdk.NucliaResource()
        
        # Crear archivo temporal para la descarga
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        # Descargar usando SDK
        resource.download_file(rid=resource_id, file_id=file_id, output=tmp_path)
        
        # Leer contenido
        with open(tmp_path, 'rb') as f:
            content = f.read()
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        # Retornar contenido y metadata
        # Nota: El SDK no devuelve headers, así que inferimos el content-type
        return {
            'content': content,
            'content_type': 'application/octet-stream',  # Por defecto
            'size': len(content)
        }
        
    except Exception as e:
        print(f"Error descargando archivo con SDK: {e}")
        raise



# ── Construcción de contexto mejorada
def build_context(
    search_json: dict, 
    max_chunks: int = 20,
    include_metadata: bool = True,
    score_threshold: float = 0.0
) -> str:
    """
    Construye contexto desde resultados de búsqueda con mejoras.
    
    Args:
        search_json: JSON de respuesta de nuclia_search
        max_chunks: Máximo de párrafos a incluir
        include_metadata: Si incluir título/fuente del documento
        score_threshold: Score mínimo para incluir un resultado (0.0-1.0)
    """
    para = (search_json.get("paragraphs") or {}).get("results", [])
    resources = (search_json.get("resources") or {})  # Información de archivos
    blocks = []
    
    for hit in para[:max_chunks]:
        # Verificar score si está disponible
        score = hit.get("score", 1.0)
        if score < score_threshold:
            continue
            
        text = (hit.get("text") or "").strip()
        if not text:
            continue
        
        # Agregar metadata si se solicita
        if include_metadata:
            resource_id = hit.get("rid", "")
            field = hit.get("field", "")
            
            # Intentar obtener información del archivo/recurso
            resource_info = resources.get(resource_id, {})
            title = resource_info.get("title", "")
            
            # Obtener número de página si está disponible
            position = hit.get("position", {})
            page_num = position.get("page_number")
            
            # Crear encabezado enriquecido con metadata
            metadata_parts = []
            if title:
                metadata_parts.append(f"📄 {title}")
            elif field:
                metadata_parts.append(f"Fuente: {field}")
            
            if page_num:
                metadata_parts.append(f"(página {page_num})")
            
            if metadata_parts:
                metadata_header = "[" + " ".join(metadata_parts) + "]\n"
                blocks.append(f"{metadata_header}{text}")
            else:
                blocks.append(text)
        else:
            blocks.append(text)
    
    return "\n\n---\n\n".join(blocks)  # Separador más visible


# ── Funciones para el endpoint /ask de Nuclia
def nuclia_ask(
    query: str,
    context: Optional[List[Dict[str, str]]] = None,
    rephrase: bool = False,
    citations: Optional[str] = None,
    filters: Optional[List[str]] = None,
    prompt: Optional[Dict[str, str]] = None,
    features: Optional[List[str]] = None,
    max_tokens: Optional[int] = None,
    synchronous: bool = True
) -> Dict[str, Any]:
    """
    Llama al endpoint /ask de Nuclia con respuestas generativas.
    
    Args:
        query: Pregunta del usuario
        context: Historial conversacional [{"author": "USER", "text": "..."}, ...]
        rephrase: Si reprocesar la pregunta con el contexto
        citations: Formato de citaciones ('default', 'llm_footnotes', None)
        filters: Filtros de búsqueda
        prompt: Prompts personalizados {"system": "...", "user": "...", "rephrase": "..."}
        features: Features de búsqueda ['keyword', 'semantic', 'relations']
        max_tokens: Número máximo de tokens en la respuesta
        synchronous: Si True devuelve respuesta completa, si False devuelve streaming
    
    Returns:
        Dict con la respuesta de Nuclia (answer, retrieval, metadata, citations, etc.)
    """
    # Construir el payload según la API de Nuclia
    ask_request = {
        "query": query
    }
    
    # Contexto conversacional para chatbot
    if context:
        ask_request["context"] = context
    
    # Reprocesar pregunta
    if rephrase:
        ask_request["rephrase"] = rephrase
    
    # Citaciones
    if citations:
        ask_request["citations"] = citations
    
    # Filtros de búsqueda
    if filters:
        ask_request["filters"] = filters
    
    # Prompts personalizados
    if prompt:
        ask_request["prompt"] = prompt
    
    # Features de búsqueda
    if features:
        ask_request["features"] = features
    
    # Max tokens
    if max_tokens:
        ask_request["max_tokens"] = max_tokens
    
    # Headers para modo síncrono
    headers = dict(HEADERS)  # Copiar headers base
    if synchronous:
        headers["x-synchronous"] = "true"
    
    # Llamar al endpoint /ask de Nuclia
    url = f"{NUCLIA_API_BASE}/kb/{KB}/ask"
    
    response = requests.post(
        url,
        headers=headers,
        json=ask_request,
        timeout=60
    )
    response.raise_for_status()
    
    # Si es síncrono, devolver JSON completo
    if synchronous:
        return response.json()
    
    # Si es streaming, devolver el generador
    return {"stream": response.iter_lines()}



def parse_nuclia_ask_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parsea la respuesta del endpoint /ask de Nuclia en modo síncrono.
    
    Returns:
        Dict con 'answer', 'sources', 'metadata', 'citations'
    """
    result = {
        "answer": "",
        "sources": [],
        "metadata": {},
        "citations": {},
        "relations": []
    }
    
    # El formato de respuesta síncrona es más directo
    if "answer" in response:
        result["answer"] = response["answer"]
    
    if "retrieval" in response:
        # Extraer fuentes de los resultados de búsqueda
        retrieval = response["retrieval"]
        if "results" in retrieval:
            sources = []
            for idx, item in enumerate(retrieval["results"]):
                source = {
                    "id": idx + 1,
                    "text": item.get("text", ""),
                    "score": item.get("score"),
                    "resource_id": item.get("rid"),
                    "field": item.get("field"),
                    "title": item.get("title", "Documento sin título")
                }
                sources.append(source)
            result["sources"] = sources
    
    if "metadata" in response:
        result["metadata"] = response["metadata"]
    
    if "citations" in response:
        result["citations"] = response["citations"]
    
    if "relations" in response:
        result["relations"] = response["relations"]
    
    return result


