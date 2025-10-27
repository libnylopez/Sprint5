# Implementación de Descarga Automática de PDFs

## Resumen de Cambios

Se implementó un sistema completo para detectar y descargar automáticamente archivos PDF (y otros tipos de archivos) desde Nuclia, todo integrado en el flujo del query sin necesidad de endpoints adicionales con permisos especiales.

## 🎯 Problema Resuelto

Antes, cuando se hacía una búsqueda, no se podía acceder directamente a los archivos PDF porque:
1. No se extraía la información de los file fields (`/f/...`)
2. No se construían URLs de descarga válidas
3. Exponer un nuevo endpoint requería permisos adicionales

## ✅ Solución Implementada

### 1. Extracción Mejorada de Fuentes (`app/agent.py`)

**Función `extract_sources_info`** ahora:

- ✅ Lee `raw_response.retrieval_results.resources` (formato de ASK endpoint)
- ✅ También soporta formato directo de SEARCH endpoint
- ✅ Detecta automáticamente archivos vs links usando el campo `icon`
- ✅ Extrae información de `data.files` para cada recurso
- ✅ Construye URLs de descarga en formato: `/kb/{KB}/resource/{RESOURCE_ID}/file/{FILE_ID}/download`
- ✅ Incluye metadata: content_type, size, filename, file_id
- ✅ Diferencia entre PDFs, Excel y otros tipos de archivos

**Estructura de respuesta mejorada:**

```json
{
  "sources": [
    {
      "id": 1,
      "title": "PDF Educación Física 2025 UVGA.pdf",
      "resource_id": "15323a97500211296cae8abeb5daec6e",
      "resource_type": "application/pdf",
      "is_downloadable": true,
      "file": {
        "download_url": "https://aws-us-east-2-1.rag.progress.cloud/api/v1/kb/{KB}/resource/{RID}/file/{FID}/download",
        "content_type": "application/pdf",
        "size": 4956786,
        "filename": "Informática (2).pdf",
        "file_id": "15323a97500211296cae8abeb5daec6e",
        "is_pdf": true,
        "is_excel": false
      },
      "text": "...",
      "score": 0.999,
      "page": 2
    }
  ]
}
```

### 2. Función de Descarga por Proxy (`app/nuclia.py`)

**Nueva función `download_resource_file`:**

```python
def download_resource_file(resource_id: str, file_id: str):
    """
    Descarga un archivo de Nuclia con streaming.
    No expone la API key al frontend.
    """
    url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{resource_id}/file/{file_id}/download"
    response = requests.get(url, headers=HEADERS, stream=True, timeout=60)
    response.raise_for_status()
    return response
```

### 3. Endpoint de Proxy (`app/main.py`)

**Nuevo endpoint `GET /download/{resource_id}/{file_id}`:**

- ✅ Hace streaming del archivo desde Nuclia
- ✅ No expone la API key de Nuclia
- ✅ No carga todo el archivo en memoria (streaming chunks)
- ✅ Preserva content-type y content-disposition
- ✅ Incluye cache headers (1 hora)

**Ejemplo de uso:**

```bash
GET /download/15323a97500211296cae8abeb5daec6e/15323a97500211296cae8abeb5daec6e
```

## 🔄 Flujo Completo

```
1. Usuario hace query → POST /ask
   ↓
2. Backend busca en Nuclia → nuclia_search()
   ↓
3. Extract sources automáticamente detecta PDFs → extract_sources_info()
   ↓
4. Construye download_url para cada archivo
   ↓
5. Respuesta incluye URLs de descarga en sources[].file.download_url
   ↓
6. Frontend puede descargar usando → GET /download/{resource_id}/{file_id}
   ↓
7. Backend hace proxy sin exponer API key
```

## 📋 Tipos de Recursos Soportados

### Archivos (icon: `application/*`)
- ✅ PDFs: `application/pdf`
- ✅ Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- ✅ Word: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- ✅ Otros archivos con content-type específico

### Links Web (icon: `application/stf-link`)
- ✅ Extrae URL original de `origin.url` o `metadata.url`
- ⚠️ Para obtener la URL completa puede requerir GET adicional al recurso

## 🧪 Testing

Se incluye `test_sources_extraction.py` que:

- ✅ Lee el `response.json` de ejemplo
- ✅ Verifica que se extraigan correctamente los recursos
- ✅ Valida que todos los archivos tengan download_url
- ✅ Muestra estadísticas: PDFs, Excel, Links, etc.
- ✅ Imprime ejemplos de URLs construidas

**Ejecutar test:**

```bash
python test_sources_extraction.py
```

## 🔑 Ventajas de Esta Implementación

1. **Sin permisos adicionales**: Usa la misma API key que el query
2. **Automático**: No requiere pasos adicionales del usuario
3. **Eficiente**: Streaming en lugar de cargar todo en memoria
4. **Seguro**: No expone la API key al frontend
5. **Completo**: Funciona con cualquier tipo de archivo
6. **Compatible**: Funciona con ambos endpoints (ASK y SEARCH)

## 📝 Ejemplo de Respuesta Completa

```json
{
  "answer": "Sí, UVG Campus Altiplano cuenta con Academia CISCO...",
  "sources": [
    {
      "id": 1,
      "title": "Informática (2).pdf",
      "text": "UVG Campus Altiplano es una de las pocas instituciones...",
      "score": 0.999,
      "page": 2,
      "resource_id": "2d65cc83db6d363db69217c482646c16",
      "resource_type": "application/pdf",
      "is_downloadable": true,
      "file": {
        "download_url": "https://aws-us-east-2-1.rag.progress.cloud/api/v1/kb/5a222e22.../resource/2d65cc.../file/2d65cc.../download",
        "content_type": "application/pdf",
        "size": 4956786,
        "filename": "Informática (2).pdf",
        "file_id": "2d65cc83db6d363db69217c482646c16",
        "is_pdf": true,
        "is_excel": false
      }
    }
  ],
  "model": "claude-4-sonnet",
  "nuclia_kb": "5a222e22-1ea8-4aad-9282-bbd025ea6412"
}
```

## 🚀 Uso en el Frontend

```javascript
// 1. Hacer query
const response = await fetch('/ask', {
  method: 'POST',
  body: JSON.stringify({ query: '¿Tiene CISCO academy?' })
});

const data = await response.json();

// 2. Mostrar fuentes con botón de descarga
data.sources.forEach(source => {
  if (source.is_downloadable) {
    const fileInfo = source.file;
    
    // Crear link de descarga
    const downloadUrl = `/download/${source.resource_id}/${fileInfo.file_id}`;
    
    // Mostrar botón
    console.log(`📥 ${source.title} (${fileInfo.size / 1024} KB)`);
    console.log(`   Descargar: ${downloadUrl}`);
  }
});
```

## 🔧 Configuración

No requiere configuración adicional. Usa las mismas variables de entorno:

```bash
NUCLIA_API_BASE=https://aws-us-east-2-1.rag.progress.cloud/api/v1
NUCLIA_API_KEY=your-api-key
KB=your-kb-id
```

## 📦 Archivos Modificados

- ✅ `app/agent.py` - Extracción mejorada de fuentes
- ✅ `app/nuclia.py` - Función de descarga por proxy
- ✅ `app/main.py` - Endpoint `/download/{resource_id}/{file_id}`
- ✅ `test_sources_extraction.py` - Script de prueba

## 🎉 Resultado

Ahora **cada vez que hagas un query**, automáticamente:
- Se detectan los PDFs y otros archivos
- Se construyen URLs de descarga válidas
- Se incluyen en la respuesta del query
- El frontend puede descargarlos sin exponer la API key

¡Todo funciona de forma automática y transparente! 🚀
