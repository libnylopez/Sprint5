# 🚀 Implementación Final con SDK de Nuclia

## ✅ Cambios Implementados

Se modificó completamente el sistema para usar el **SDK oficial de Python de Nuclia** en lugar de hacer requests manuales. Ahora el agente obtiene automáticamente URLs temporales de descarga con token incluido.

---

## 🔑 Características Clave

### 1. **Uso del SDK de Nuclia** 
- ✅ `NucliaResource().get(rid=...)` para obtener información del recurso
- ✅ `NucliaResource().temporal_download_url(rid=..., file_id=..., ttl=3600)` para URLs temporales
- ✅ URLs con token temporal incluido (válidas por 1 hora)
- ✅ **No requiere autenticación adicional desde el frontend**

### 2. **Proceso Automático en el Query**
```
Query → Nuclia Search → Detect Files → SDK Get Resource → SDK Get Temporal URL → Response
```

### 3. **URLs Temporales vs URLs Estándar**

**Antes (con requests):**
```
https://aws-us-east-2-1.rag.progress.cloud/api/v1/kb/{KB}/resource/{RID}/file/{FID}/download
```
❌ Requiere header `x-api-key` para descargar
❌ Expone la API key si se usa desde el frontend

**Ahora (con SDK):**
```
https://aws-us-east-2-1.rag.progress.cloud/api/v1/kb/{KB}/resource/{RID}/file/{FID}/download?token=TEMPORAL_TOKEN_HERE
```
✅ Token temporal incluido en la URL
✅ **No requiere headers de autenticación**
✅ Válido por 1 hora (configurable)
✅ Frontend puede usar directamente con `fetch(url)`

---

## 📝 Código Implementado

### 1. SDK Inicializado (`app/nuclia.py`)

```python
from nuclia import sdk

# Inicializar SDK al importar el módulo
def _init_nuclia_sdk():
    try:
        sdk.NucliaAuth().kb(KB)
        return True
    except Exception as e:
        print(f"Warning: No se pudo inicializar SDK de Nuclia: {e}")
        return False

_SDK_INITIALIZED = _init_nuclia_sdk()
```

### 2. Obtener Recurso con SDK

```python
def get_nuclia_resource(resource_id: str) -> dict:
    """Obtiene información completa usando el SDK."""
    resource = sdk.NucliaResource()
    data = resource.get(rid=resource_id, show=["basic", "values", "origin"])
    return data
```

### 3. Obtener URL Temporal

```python
def get_temporal_download_url(resource_id: str, file_id: str, ttl: int = 3600) -> str:
    """
    Obtiene URL temporal con token incluido.
    No requiere autenticación adicional para descargar.
    """
    resource = sdk.NucliaResource()
    url = resource.temporal_download_url(rid=resource_id, file_id=file_id, ttl=ttl)
    return url
```

### 4. Extracción Automática en el Agent (`app/agent.py`)

```python
def extract_sources_info(search_json: dict, max_chunks: int = 20, score_threshold: float = 0.0) -> list:
    # ... código de extracción ...
    
    # Para cada archivo (NO links):
    if is_file and resource_id:
        # 1. Obtener recurso completo con SDK
        resource_details = get_nuclia_resource(resource_id)
        
        # 2. Extraer información del archivo
        files = resource_details.get("data", {}).get("files", {})
        for file_id, file_info in files.items():
            # 3. Obtener URL temporal de descarga con SDK
            temporal_url = get_temporal_download_url(resource_id, file_id, ttl=3600)
            
            # 4. Agregar a la respuesta
            file_download_info = {
                "download_url": temporal_url,  # URL con token incluido
                "content_type": content_type,
                "size": file_size,
                "filename": filename,
                "file_id": file_id,
                "is_pdf": "pdf" in content_type.lower(),
                "is_excel": "sheet" in content_type.lower(),
                "ttl": 3600  # Válida por 1 hora
            }
```

---

## 🎯 Flujo Completo

```
1. Usuario hace query
   POST /ask?query=UVG+CISCO

2. Backend busca en Nuclia
   nuclia_search(query)

3. Por cada archivo en los resultados:
   a) SDK obtiene info del recurso
      resource = sdk.NucliaResource().get(rid=resource_id)
   
   b) SDK genera URL temporal
      url = sdk.NucliaResource().temporal_download_url(rid, file_id, ttl=3600)
   
   c) URL incluye token: 
      https://.../download?token=TEMP_TOKEN

4. Respuesta incluye URLs temporales
   {
     "sources": [
       {
         "file": {
           "download_url": "https://...?token=...",
           "ttl": 3600
         }
       }
     ]
   }

5. Frontend usa URL directamente
   fetch(source.file.download_url)  // No requiere headers!
     .then(r => r.blob())
     .then(blob => {
       // Descargar archivo
     })
```

---

## 🔐 Seguridad

### ✅ Ventajas de URLs Temporales

1. **No expone API key**: Token temporal en lugar de API key permanente
2. **TTL configurable**: Expira automáticamente después de 1 hora
3. **No requiere proxy**: Frontend puede descargar directamente
4. **Auditable**: Cada URL tiene su propio token temporal
5. **Revocable**: Si el token se compromete, expira en 1 hora

### 🔒 Comparación de Seguridad

| Método | API Key Expuesta | Requiere Proxy | TTL | Seguridad |
|--------|------------------|----------------|-----|-----------|
| **Requests manuales** | ⚠️ Sí (en headers) | ✅ Sí | ♾️ Permanente | ⚠️ Baja |
| **SDK + Temporal URL** | ✅ No | ❌ No | ⏱️ 1 hora | ✅ Alta |

---

## 📦 Dependencias Actualizadas

### `requirements.txt`
```txt
fastapi>=0.110
uvicorn[standard]>=0.27
requests>=2.31
anthropic>=0.30
python-dotenv>=1.0
pydantic>=2.6
nuclia>=3.0  # ✨ NUEVO
```

### Instalación
```bash
pip install -r requirements.txt
```

---

## 🧪 Testing

### Script de Prueba: `test_sources_extraction.py`

```bash
python test_sources_extraction.py
```

**Este test:**
- ✅ Hace llamadas reales al SDK de Nuclia
- ✅ Obtiene URLs temporales de descarga
- ✅ Verifica que incluyan tokens
- ✅ Muestra TTL y metadata completa

**Ejemplo de salida:**
```
================================================================================
TEST: Extracción con SDK de Nuclia - URLs Temporales de Descarga
================================================================================

⚠️  NOTA: Este test hace llamadas reales a la API de Nuclia

✅ Se extrajeron 10 fuentes

============================================================
Fuente #1
============================================================
Título: Informática (2).pdf
Tipo: application/pdf

📥 ARCHIVO DESCARGABLE (con URL temporal):
  - URL Temporal: https://aws-us-east-2-1.rag.progress.cloud/.../download?token=eyJ...
  - Content Type: application/pdf
  - Tamaño: 4956786 bytes (4841.59 KB)
  - TTL: 3600 segundos
  - Es PDF: ✅
  ✅ URL contiene token temporal

💡 EJEMPLO DE USO
================================================================================
Esta URL puede usarse directamente desde el frontend:
   fetch('https://.../download?token=eyJ...')
     .then(r => r.blob())
     .then(blob => {
       // Descargar archivo
     })

✅ TEST COMPLETADO
```

---

## 💡 Uso en el Frontend

### Ejemplo Simple (Vanilla JS)

```javascript
// 1. Hacer query
const response = await fetch('/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    query: '¿Tiene CISCO academy?' 
  })
});

const data = await response.json();

// 2. Descargar archivos directamente (sin headers!)
data.sources.forEach(async source => {
  if (source.is_downloadable) {
    const fileUrl = source.file.download_url;
    
    // ✅ No requiere x-api-key header!
    const fileResponse = await fetch(fileUrl);
    const blob = await fileResponse.blob();
    
    // Crear link de descarga
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = source.file.filename;
    a.click();
    URL.revokeObjectURL(url);
  }
});
```

### Ejemplo con React

```jsx
function DownloadButton({ source }) {
  const handleDownload = async () => {
    try {
      // URL temporal ya incluye el token
      const response = await fetch(source.file.download_url);
      const blob = await response.blob();
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = source.file.filename;
      a.click();
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error descargando:', error);
    }
  };
  
  return (
    <button onClick={handleDownload}>
      📥 {source.file.filename} ({(source.file.size / 1024).toFixed(2)} KB)
      <span className="ttl">Válido por 1h</span>
    </button>
  );
}
```

---

## 🔄 Migración del Código Anterior

### ❌ Antes (Requests manuales)

```python
# ❌ Requería hacer request manual
url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{rid}/file/{fid}/download"
response = requests.get(url, headers={"x-api-key": NUCLIA_TOKEN})

# ❌ Necesitaba proxy para no exponer API key
@app.get("/download/{rid}/{fid}")
def download_file(rid, fid):
    nuclia_response = requests.get(nuclia_url, headers=HEADERS, stream=True)
    return StreamingResponse(nuclia_response.iter_content())
```

### ✅ Ahora (SDK de Nuclia)

```python
# ✅ SDK obtiene URL temporal con token incluido
from nuclia import sdk

resource = sdk.NucliaResource()
temporal_url = resource.temporal_download_url(rid=rid, file_id=fid, ttl=3600)

# ✅ URL puede usarse directamente desde el frontend
# https://.../download?token=TEMPORAL_TOKEN
# No requiere proxy ni headers adicionales
```

---

## 📊 Estructura de Respuesta Actualizada

```json
{
  "answer": "Sí, UVG Campus Altiplano cuenta con Academia CISCO...",
  "sources": [
    {
      "id": 1,
      "title": "Informática (2).pdf",
      "resource_id": "2d65cc83db6d363db69217c482646c16",
      "resource_type": "application/pdf",
      "is_downloadable": true,
      "file": {
        "download_url": "https://aws-us-east-2-1.rag.progress.cloud/api/v1/kb/5a222e22.../resource/2d65cc.../file/2d65cc.../download?token=eyJhbGc...",
        "content_type": "application/pdf",
        "size": 4956786,
        "filename": "Informática (2).pdf",
        "file_id": "2d65cc83db6d363db69217c482646c16",
        "is_pdf": true,
        "is_excel": false,
        "ttl": 3600
      },
      "text": "...",
      "score": 0.999,
      "page": 2
    }
  ],
  "model": "claude-4-sonnet"
}
```

**Nota:** El campo `download_url` ahora incluye `?token=...` al final.

---

## ⚡ Optimizaciones Implementadas

### 1. Cache de Recursos
```python
resources_cache = {}

if resource_id not in resources_cache:
    resource_details = get_nuclia_resource(resource_id)
    resources_cache[resource_id] = resource_details
```

✅ Evita múltiples llamadas al SDK para el mismo recurso

### 2. Logs de Debugging
```python
print(f"🔍 Obteniendo información del recurso {resource_id} usando SDK...")
print(f"📥 Obteniendo URL temporal de descarga para {file_id}...")
```

✅ Facilita el debugging y monitoreo

### 3. Fallback a Requests
```python
try:
    # Intentar con SDK
    data = sdk.NucliaResource().get(rid=resource_id)
except Exception:
    # Fallback a requests manual
    r = requests.get(url, headers=HEADERS)
    data = r.json()
```

✅ Garantiza funcionamiento incluso si el SDK falla

---

## 🎉 Ventajas Finales

| Feature | Implementación |
|---------|----------------|
| **Automático** | ✅ Todo ocurre en el query |
| **Seguro** | ✅ Tokens temporales, no API key |
| **Eficiente** | ✅ Cache de recursos |
| **Simple** | ✅ Frontend solo hace fetch(url) |
| **SDK Oficial** | ✅ Usa SDK de Nuclia |
| **URLs Temporales** | ✅ Token incluido, TTL 1 hora |
| **Sin Proxy** | ✅ No requiere endpoint adicional |
| **Revocable** | ✅ Tokens expiran automáticamente |

---

## 🚀 ¡Listo para Producción!

**Ahora cada query automáticamente:**
1. ✅ Detecta archivos (PDFs, Excel, etc.)
2. ✅ Usa SDK para obtener información completa
3. ✅ Genera URLs temporales con token incluido
4. ✅ Frontend puede descargar sin autenticación adicional
5. ✅ Tokens expiran en 1 hora automáticamente

**Todo esto sin exponer la API key y de forma completamente automática! 🎊**
