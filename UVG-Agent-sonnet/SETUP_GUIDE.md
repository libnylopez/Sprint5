# 🚀 Guía de Setup - SDK de Nuclia

## Instalación y Configuración

### 1️⃣ Instalar Dependencias

```bash
# Activar virtual environment (si lo usas)
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Instalar requirements (incluye nuclia>=3.0)
pip install -r requirements.txt
```

### 2️⃣ Verificar Variables de Entorno

Asegúrate de tener estas variables en tu `.env`:

```bash
# Nuclia Configuration
NUCLIA_API_BASE=https://aws-us-east-2-1.rag.progress.cloud/api/v1
NUCLIA_TOKEN=tu-api-key-aqui
KB=tu-kb-id-aqui

# Claude Configuration
ANTHROPIC_KEY=tu-anthropic-key-aqui
CLAUDE_MODEL=claude-sonnet-4-20250514
```

### 3️⃣ Verificar Instalación del SDK

```bash
python -c "from nuclia import sdk; print('✅ SDK de Nuclia instalado correctamente')"
```

Si ves el mensaje de éxito, estás listo. Si hay error:

```bash
pip install --upgrade nuclia
```

---

## 🧪 Testing

### Test Rápido (Sin llamadas API)

```bash
python -c "
from app.config import KB, NUCLIA_TOKEN
print(f'KB: {KB[:10]}...')
print(f'Token: {NUCLIA_TOKEN[:10]}...')
print('✅ Configuración OK')
"
```

### Test Completo (Con llamadas al SDK)

```bash
python test_sources_extraction.py
```

**Este test:**
- Lee `response.json` con datos de ejemplo
- Hace llamadas reales al SDK de Nuclia
- Obtiene URLs temporales de descarga
- Verifica que incluyan tokens

**Salida esperada:**
```
================================================================================
TEST: Extracción con SDK de Nuclia - URLs Temporales de Descarga
================================================================================

✅ Se extrajeron 10 fuentes

📥 ARCHIVO DESCARGABLE (con URL temporal):
  - URL Temporal: https://aws-us-east-2-1.rag.progress.cloud/.../download?token=eyJ...
  - TTL: 3600 segundos
  ✅ URL contiene token temporal

✅ Todos los archivos descargables tienen download_url
✅ Se obtuvieron 5 URLs temporales de descarga
✅ TEST COMPLETADO
```

---

## 🚀 Iniciar el Servidor

```bash
uvicorn app.main:app --reload --port 8000
```

**Endpoints disponibles:**
- `GET /health` - Health check
- `POST /ask` - Query principal (incluye URLs temporales automáticamente)
- `POST /nuclia-ask` - Query con LLM de Nuclia
- ~~`GET /download/{rid}/{fid}`~~ - **YA NO ES NECESARIO** (URLs temporales)

---

## 🧪 Probar el Endpoint

### Con cURL

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "UVG Altiplano tiene CISCO academy?",
    "size": 30,
    "max_chunks": 20
  }' | jq
```

### Con Python

```python
import requests

response = requests.post(
    'http://localhost:8000/ask',
    json={
        'query': 'UVG Altiplano tiene CISCO academy?',
        'size': 30,
        'max_chunks': 20
    }
)

data = response.json()

print(f"Respuesta: {data['answer']}")
print(f"\nFuentes con archivos descargables:")

for source in data['sources']:
    if source.get('is_downloadable'):
        file_info = source['file']
        print(f"\n📥 {source['title']}")
        print(f"   URL: {file_info['download_url'][:80]}...")
        print(f"   TTL: {file_info['ttl']} segundos")
```

### Con HTTPie (alternativa a cURL)

```bash
http POST localhost:8000/ask query="UVG CISCO academy" size:=30
```

---

## 🔍 Debugging

### 1. Ver logs del SDK

El código imprime logs útiles:

```
🔍 Obteniendo información del recurso 2d65cc83... usando SDK...
📥 Obteniendo URL temporal de descarga para 2d65cc83...
```

### 2. Verificar SDK inicializado

```python
from app.nuclia import _SDK_INITIALIZED
print(f"SDK Inicializado: {_SDK_INITIALIZED}")
```

### 3. Probar SDK manualmente

```python
from nuclia import sdk

# Obtener recurso
resource = sdk.NucliaResource()
data = resource.get(rid="tu-resource-id", show=["basic", "values"])
print(data)

# Obtener URL temporal
url = resource.temporal_download_url(
    rid="tu-resource-id",
    file_id="tu-file-id",
    ttl=3600
)
print(f"URL temporal: {url}")
```

---

## ⚠️ Troubleshooting

### Error: "Module 'nuclia' not found"

```bash
pip install nuclia>=3.0
```

### Error: "Authentication failed"

Verifica que `NUCLIA_TOKEN` en `.env` sea correcto:

```bash
echo $NUCLIA_TOKEN  # Linux/Mac
echo %NUCLIA_TOKEN%  # Windows
```

### Error: "KB not found"

Verifica que `KB` en `.env` sea correcto:

```bash
echo $KB  # Linux/Mac
echo %KB%  # Windows
```

### Warning: "No se pudo inicializar SDK de Nuclia"

Verifica:
1. ✅ `nuclia` está instalado
2. ✅ `NUCLIA_TOKEN` está configurado
3. ✅ `KB` está configurado
4. ✅ Token tiene permisos para el KB

### Error: "temporal_download_url() failed"

Si el SDK falla al generar URLs temporales:
1. Verifica que el token tenga permisos
2. El código tiene fallback a URL estándar (pero requiere autenticación)

---

## 📁 Estructura del Proyecto

```
UVG-Agent-sonnet/
├── app/
│   ├── __init__.py
│   ├── agent.py          # 🔄 Modificado - Usa SDK
│   ├── clients.py
│   ├── config.py
│   ├── llm.py
│   ├── main.py           # 🔄 Modificado - Endpoint /download opcional
│   ├── nuclia.py         # 🔄 Modificado - SDK de Nuclia
│   ├── schemas.py
│   └── settings.py
├── requirements.txt       # 🔄 Modificado - Agregado nuclia>=3.0
├── test_sources_extraction.py  # 🔄 Modificado - Test con SDK
├── response.json         # Datos de ejemplo
├── .env                  # Configuración (no en git)
├── IMPLEMENTACION_SDK_NUCLIA.md  # ✨ Nuevo - Documentación
└── RESUMEN_FINAL_SDK.md  # ✨ Nuevo - Resumen
```

---

## 🎯 Checklist de Verificación

Antes de usar en producción:

- [ ] ✅ SDK de Nuclia instalado (`pip list | grep nuclia`)
- [ ] ✅ Variables de entorno configuradas (`.env`)
- [ ] ✅ Test pasa correctamente (`python test_sources_extraction.py`)
- [ ] ✅ Servidor inicia sin errores (`uvicorn app.main:app`)
- [ ] ✅ Endpoint `/ask` responde correctamente
- [ ] ✅ URLs temporales incluyen `?token=...`
- [ ] ✅ Frontend puede descargar sin headers

---

## 🚀 Deploy

### Variables de Entorno (Producción)

```bash
NUCLIA_API_BASE=https://aws-us-east-2-1.rag.progress.cloud/api/v1
NUCLIA_TOKEN=tu-production-api-key
KB=tu-production-kb-id
ANTHROPIC_KEY=tu-production-anthropic-key
CLAUDE_MODEL=claude-sonnet-4-20250514
```

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY .env .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t uvg-agent .
docker run -p 8000:8000 --env-file .env uvg-agent
```

---

## 📞 Soporte

### Documentación Oficial de Nuclia
- SDK: https://docs.rag.progress.cloud/docs/develop/python-sdk/kb/
- API: https://docs.rag.progress.cloud/docs/api

### Issues Comunes

1. **SDK no inicializa**: Revisar credenciales en `.env`
2. **URLs no tienen token**: Verificar permisos del token de API
3. **Descargas fallan**: Verificar que TTL no haya expirado (1 hora)

---

## ✅ Todo Listo

Si llegaste aquí y todo funciona:

🎉 **¡Felicidades! Tu agente está listo para usar con el SDK de Nuclia y URLs temporales de descarga.**

```bash
# Inicia el servidor
uvicorn app.main:app --reload

# En otra terminal, prueba
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "UVG CISCO academy"}' | jq
```

¡Disfruta de tu RAG agent con descarga automática de PDFs! 🚀
