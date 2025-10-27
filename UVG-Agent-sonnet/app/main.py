# app/main.py
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .schemas import AskBody, NucliaAskBody
from .agent import ask_agent
from .nuclia import nuclia_ask, parse_nuclia_ask_response, download_resource_file
from .config import CLAUDE_MODEL, KB

# ── API HTTP
app = FastAPI(title="UVG Agent (Nuclia + Claude)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(body: AskBody):
    try:
        result = ask_agent(
            body.query,
            size=body.size or 30,
            max_chunks=body.max_chunks or 20,
            use_semantic=body.use_semantic if body.use_semantic is not None else True,
            min_score=body.min_score or 0.0,
        )
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "model": CLAUDE_MODEL,
            "nuclia_kb": KB,
            "params": {
                "size": body.size or 30, 
                "max_chunks": body.max_chunks or 20,
                "use_semantic": body.use_semantic if body.use_semantic is not None else True,
                "min_score": body.min_score or 0.0
            },
        }
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else 502
        detail = e.response.text[:600] if e.response is not None else str(e)
        raise HTTPException(status_code=502, detail=f"Error consultando Nuclia ({status}): {detail}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error llamando a Claude: {e}")


@app.post("/nuclia-ask")
def nuclia_ask_endpoint(body: NucliaAskBody):
    """
    Endpoint que usa directamente el /ask de Nuclia con su LLM generativo.
    Soporta contexto conversacional para chatbots y prompts personalizados.
    """
    try:
        # Convertir contexto a formato esperado por Nuclia
        context = None
        if body.context:
            context = [{"author": ctx.author, "text": ctx.text} for ctx in body.context]
        
        # Convertir prompt a dict
        prompt = None
        if body.prompt:
            prompt = {}
            if body.prompt.system:
                prompt["system"] = body.prompt.system
            if body.prompt.user:
                prompt["user"] = body.prompt.user
            if body.prompt.rephrase:
                prompt["rephrase"] = body.prompt.rephrase
        
        # Llamar a Nuclia
        raw_response = nuclia_ask(
            query=body.query,
            context=context,
            rephrase=body.rephrase or False,
            citations=body.citations,
            filters=body.filters,
            prompt=prompt,
            features=body.features,
            max_tokens=body.max_tokens,
            synchronous=body.synchronous if body.synchronous is not None else True
        )
        
        # Parsear respuesta
        parsed = parse_nuclia_ask_response(raw_response)
        
        return {
            "answer": parsed["answer"],
            "sources": parsed["sources"],
            "metadata": parsed["metadata"],
            "citations": parsed["citations"],
            "relations": parsed["relations"],
            "nuclia_kb": KB,
            "params": {
                "rephrase": body.rephrase or False,
                "citations": body.citations,
                "synchronous": body.synchronous if body.synchronous is not None else True,
                "features": body.features
            },
            "raw_response": raw_response  # Para debugging
        }
        
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else 502
        detail = e.response.text[:600] if e.response is not None else str(e)
        raise HTTPException(
            status_code=status, 
            detail=f"Error en endpoint /ask de Nuclia ({status}): {detail}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando solicitud: {str(e)}")


@app.get("/download/{resource_id}/{file_id}")
async def download_file(resource_id: str, file_id: str):
    """
    Endpoint proxy para descargar archivos de recursos de Nuclia usando el SDK.
    No expone la API key al frontend.
    
    Args:
        resource_id: ID del recurso en Nuclia
        file_id: ID del archivo (file field ID)
    
    Returns:
        StreamingResponse con el archivo
    """
    try:
        # Obtener el archivo desde Nuclia usando SDK
        file_data = download_resource_file(resource_id, file_id)
        
        # El SDK devuelve un dict con 'content', 'content_type', 'size'
        content = file_data['content']
        content_type = file_data.get('content_type', 'application/octet-stream')
        
        # Construir nombre de archivo
        content_disposition = f'attachment; filename="{resource_id}_{file_id}.pdf"'
        
        # Crear un generador para streaming desde bytes
        def iter_bytes():
            chunk_size = 8192
            for i in range(0, len(content), chunk_size):
                yield content[i:i + chunk_size]
        
        # Retornar como StreamingResponse
        return StreamingResponse(
            iter_bytes(),
            media_type=content_type,
            headers={
                "Content-Disposition": content_disposition,
                "Content-Length": str(len(content)),
                "Cache-Control": "private, max-age=3600",  # Cache por 1 hora
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error descargando archivo: {str(e)}"
        )


