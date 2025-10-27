from .llm import preprocess_query
from .nuclia import nuclia_search, build_context, get_nuclia_resource, get_temporal_download_url, download_resource_file
from .clients import client
from .config import CLAUDE_MODEL, INSTRUCTIONS

# ── Orquestación mejorada
def ask_agent(
    question: str, 
    *, 
    size: int = 30, 
    max_chunks: int = 20,
    use_semantic: bool = True,
    min_score: float = 0.0
) -> dict:
    """
    Orquesta el pipeline RAG completo con mejoras.
    
    Args:
        question: Pregunta del usuario
        size: Resultados a obtener de Nuclia
        max_chunks: Máximo de párrafos para el contexto
        use_semantic: Si usar búsqueda semántica (además de keyword)
        min_score: Score mínimo para incluir resultados
    
    Returns:
        dict con 'answer', 'sources' y 'search_results'
    """
    # 1. Preprocesar la consulta
    consulta = preprocess_query(question)
    
    # 2. Búsqueda híbrida (keyword + semantic)
    features = ["keyword"]
    if use_semantic:
        features.append("semantic")
    
    search = nuclia_search(
        consulta, 
        size=size,
        features=features,
        min_score=min_score
    )
    
    # 3. Construir contexto con metadata
    context = build_context(
        search, 
        max_chunks=max_chunks,
        include_metadata=True,
        score_threshold=min_score
    )

    # 4. Generar respuesta con Claude
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        temperature=0.2,
        system=INSTRUCTIONS,
        messages=[{"role": "user", "content": f"Pregunta: {question}\n\nContexto:\n{context}"}],
    )
    parts = response.content or []
    answer = "".join(getattr(p, "text", "") for p in parts)
    
    # 5. Extraer información de fuentes para el frontend
    sources_info = extract_sources_info(search, max_chunks, min_score)
    
    return {
        "answer": answer,
        "sources": sources_info,
        "search_results": search  # Resultados completos para referencia
    }


def extract_sources_info(search_json: dict, max_chunks: int = 20, score_threshold: float = 0.0) -> list:
    """
    Extrae información estructurada de las fuentes para mostrar en el frontend.
    Automáticamente obtiene URLs temporales de descarga para archivos usando el SDK de Nuclia.
    
    IMPORTANTE: Esta función funciona con respuestas de:
    - Endpoint /ask (nuclia_search): retrieval_results en nivel superior
    - Endpoint /nuclia-ask (ASK de Nuclia): raw_response.retrieval_results
    
    Returns:
        Lista de diccionarios con información de cada fuente
    """
    # Extraer recursos y párrafos según el formato
    retrieval_results = None
    
    # Formato 1: raw_response (de /nuclia-ask)
    raw_response = search_json.get("raw_response", {})
    if raw_response:
        retrieval_results = raw_response.get("retrieval_results", {})
    
    # Formato 2: retrieval en raw_response (otro formato de ASK)
    if not retrieval_results and raw_response:
        retrieval = raw_response.get("retrieval", {})
        retrieval_results = retrieval.get("results", {}) if isinstance(retrieval, dict) else {}
    
    # Formato 3: nivel superior (de /ask con nuclia_search)
    if not retrieval_results:
        retrieval_results = search_json
    
    # Obtener recursos con su información básica
    resources = retrieval_results.get("resources", {})
    
    # Obtener párrafos
    para = (retrieval_results.get("paragraphs") or {}).get("results", [])
    sources = []
    
    # Cache para recursos ya obtenidos del SDK (evitar llamadas duplicadas)
    resources_cache = {}
    
    for idx, hit in enumerate(para[:max_chunks]):
        score = hit.get("score", 0.0)
        if score < score_threshold:
            continue
            
        text = (hit.get("text") or "").strip()
        if not text:
            continue
        
        resource_id = hit.get("rid", "")
        field = hit.get("field", "")
        
        # Información básica del recurso desde retrieval_results
        resource_info = resources.get(resource_id, {})
        title = resource_info.get("title", "Documento sin título")
        icon = resource_info.get("icon", "")
        
        # Inicializar variables
        url = ""
        file_download_info = None
        
        # 1. Detectar tipo de recurso por icon
        is_file = icon and "application/" in icon and icon != "application/stf-link"
        is_link = icon == "application/stf-link"
        
        # 2. Para archivos: SIEMPRE obtener del SDK (no confiar en retrieval_results)
        if is_file and resource_id:
            try:
                # Usar cache para evitar múltiples llamadas al mismo recurso
                if resource_id not in resources_cache:
                    print(f"🔍 Obteniendo recurso {resource_id} con SDK...")
                    resource_details = get_nuclia_resource(resource_id)
                    resources_cache[resource_id] = resource_details
                else:
                    resource_details = resources_cache[resource_id]
                
                # Buscar file fields en data.files del recurso completo
                data = resource_details.get("data", {})
                files = data.get("files", {})
                
                # Procesar archivos disponibles
                for file_id, file_info in files.items():
                    file_value = file_info.get("value", {})
                    file_data = file_value.get("file", {})
                    
                    content_type = file_data.get("content_type", "")
                    file_size = file_data.get("size", 0)
                    filename = file_data.get("filename", title)
                    
                    if content_type:  # Si hay información del archivo
                        # Obtener URL temporal de descarga usando SDK
                        print(f"📥 Obteniendo URL temporal para {file_id}...")
                        temporal_url = get_temporal_download_url(resource_id, file_id, ttl=3600)
                        
                        file_download_info = {
                            "download_url": temporal_url,
                            "content_type": content_type,
                            "size": file_size,
                            "filename": filename,
                            "file_id": file_id,
                            "is_pdf": "pdf" in content_type.lower(),
                            "is_excel": "sheet" in content_type.lower() or "excel" in content_type.lower(),
                            "ttl": 3600  # 1 hora de validez
                        }
                        
                        url = temporal_url
                        break  # Usar el primer archivo encontrado
                        
            except Exception as e:
                print(f"⚠️ Error obteniendo archivo para recurso {resource_id}: {e}")
                # Continuar sin información de descarga
                pass
        
        # 3. Para links, intentar obtener la URL original
        elif is_link:
            # Intentar de origin
            origin = resource_info.get("origin", {})
            if isinstance(origin, dict):
                url = origin.get("url", "") or origin.get("path", "")
            
            # Si no, intentar de metadata
            if not url:
                metadata = resource_info.get("metadata", {})
                if isinstance(metadata, dict):
                    url = metadata.get("uri", "") or metadata.get("url", "")
        
        # 4. Fallback: si no hay URL, usar referencia al recurso
        if not url and resource_id:
            from .config import NUCLIA_API_BASE, KB
            url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{resource_id}"

        
        # Número de página
        position = hit.get("position", {})
        page_num = position.get("page_number")
        
        # Determinar tipo de URL y de recurso
        url_type = "none"
        resource_type = icon if icon else "unknown"
        
        if url:
            if "http://" in url or "https://" in url:
                if "nuclia" in url or "rag.progress.cloud" in url:
                    url_type = "nuclia"  # URL interna de Nuclia
                else:
                    url_type = "external"  # URL externa/original
            else:
                url_type = "resource"  # ID de recurso
        
        # Construir objeto de fuente
        source = {
            "id": idx + 1,
            "title": title,
            "text": text,
            "score": round(score, 3) if score else None,
            "page": page_num,
            "field": field,
            "resource_id": resource_id,
            "url": url,  # URL para abrir el documento
            "url_type": url_type,  # Tipo de URL
            "resource_type": resource_type,  # Tipo de recurso (MIME type o icon)
            "has_url": bool(url),  # Flag para saber si hay URL disponible
        }
        
        # Agregar información de descarga si está disponible (PDF, Excel, etc.)
        if file_download_info:
            source["file"] = file_download_info
            source["is_downloadable"] = True
        else:
            source["is_downloadable"] = False

        
        sources.append(source)
    
    return sources

