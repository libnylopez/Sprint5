# 🎨 Guía de Integración Frontend

## Ejemplos de Código para Usar la API con Descarga de PDFs

---

## 📡 1. JavaScript/Fetch (Vanilla JS)

### Hacer Query y Obtener Archivos

```javascript
async function askQuestion(query) {
  try {
    // 1. Hacer la consulta
    const response = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        size: 30,
        max_chunks: 20,
        use_semantic: true,
        min_score: 0.0
      })
    });
    
    const data = await response.json();
    
    // 2. Mostrar respuesta
    console.log('Respuesta:', data.answer);
    
    // 3. Procesar fuentes con archivos descargables
    data.sources.forEach(source => {
      console.log(`\n📄 ${source.title}`);
      console.log(`Score: ${source.score}`);
      
      if (source.is_downloadable) {
        const file = source.file;
        console.log(`✅ Archivo descargable:`);
        console.log(`   - Tipo: ${file.content_type}`);
        console.log(`   - Tamaño: ${(file.size / 1024).toFixed(2)} KB`);
        console.log(`   - Descargar: /download/${source.resource_id}/${file.file_id}`);
        
        if (file.is_pdf) {
          console.log(`   📕 Es un PDF`);
        }
        if (file.is_excel) {
          console.log(`   📊 Es un Excel`);
        }
      }
    });
    
    return data;
    
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Uso
askQuestion('¿UVG Altiplano tiene Academia CISCO?');
```

### Crear Botones de Descarga Dinámicamente

```javascript
function renderSources(sources, containerId) {
  const container = document.getElementById(containerId);
  
  sources.forEach(source => {
    const sourceDiv = document.createElement('div');
    sourceDiv.className = 'source-item';
    
    // Título
    const title = document.createElement('h3');
    title.textContent = source.title;
    sourceDiv.appendChild(title);
    
    // Texto
    const text = document.createElement('p');
    text.textContent = source.text.substring(0, 200) + '...';
    sourceDiv.appendChild(text);
    
    // Botón de descarga si es archivo
    if (source.is_downloadable) {
      const file = source.file;
      const downloadBtn = document.createElement('a');
      downloadBtn.href = `/download/${source.resource_id}/${file.file_id}`;
      downloadBtn.download = file.filename;
      downloadBtn.className = 'btn-download';
      
      // Icono según tipo
      const icon = file.is_pdf ? '📕' : file.is_excel ? '📊' : '📄';
      downloadBtn.innerHTML = `${icon} Descargar ${file.filename} (${(file.size / 1024).toFixed(2)} KB)`;
      
      sourceDiv.appendChild(downloadBtn);
    } else if (source.url && source.resource_type === 'application/stf-link') {
      // Enlace externo
      const link = document.createElement('a');
      link.href = source.url;
      link.target = '_blank';
      link.className = 'btn-external';
      link.innerHTML = '🔗 Abrir enlace';
      sourceDiv.appendChild(link);
    }
    
    container.appendChild(sourceDiv);
  });
}
```

---

## ⚛️ 2. React

### Hook Personalizado

```jsx
import { useState, useCallback } from 'react';

function useUVGAgent() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  
  const ask = useCallback(async (query, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          size: options.size || 30,
          max_chunks: options.maxChunks || 20,
          use_semantic: options.useSemanctic !== false,
          min_score: options.minScore || 0.0
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
      return result;
      
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return { ask, loading, error, data };
}

export default useUVGAgent;
```

### Componente de Fuente con Descarga

```jsx
import React from 'react';

function SourceItem({ source }) {
  return (
    <div className="source-card">
      <h3>{source.title}</h3>
      
      {source.page && (
        <span className="badge">Página {source.page}</span>
      )}
      
      <p className="source-text">
        {source.text}
      </p>
      
      {source.score && (
        <div className="score">
          Relevancia: {(source.score * 100).toFixed(1)}%
        </div>
      )}
      
      {source.is_downloadable && (
        <DownloadButton
          resourceId={source.resource_id}
          fileInfo={source.file}
        />
      )}
      
      {source.resource_type === 'application/stf-link' && (
        <a 
          href={source.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="btn-link"
        >
          🔗 Abrir enlace
        </a>
      )}
    </div>
  );
}

function DownloadButton({ resourceId, fileInfo }) {
  const downloadUrl = `/download/${resourceId}/${fileInfo.file_id}`;
  const sizeKB = (fileInfo.size / 1024).toFixed(2);
  
  const icon = fileInfo.is_pdf ? '📕' : 
               fileInfo.is_excel ? '📊' : '📄';
  
  return (
    <a 
      href={downloadUrl}
      download={fileInfo.filename}
      className="btn-download"
    >
      {icon} Descargar {fileInfo.filename}
      <span className="file-size">({sizeKB} KB)</span>
    </a>
  );
}

export { SourceItem, DownloadButton };
```

### Componente Principal

```jsx
import React, { useState } from 'react';
import useUVGAgent from './hooks/useUVGAgent';
import { SourceItem } from './components/SourceItem';

function ChatInterface() {
  const [query, setQuery] = useState('');
  const { ask, loading, error, data } = useUVGAgent();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    await ask(query);
  };
  
  return (
    <div className="chat-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Pregunta sobre UVG..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Buscando...' : 'Preguntar'}
        </button>
      </form>
      
      {error && (
        <div className="error">
          ❌ Error: {error}
        </div>
      )}
      
      {data && (
        <>
          <div className="answer">
            <h2>Respuesta</h2>
            <p>{data.answer}</p>
          </div>
          
          <div className="sources">
            <h2>Fuentes ({data.sources.length})</h2>
            {data.sources.map((source, idx) => (
              <SourceItem key={idx} source={source} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default ChatInterface;
```

---

## 🎨 3. CSS Ejemplo

```css
.source-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.source-card h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 8px;
}

.source-text {
  color: #666;
  line-height: 1.6;
  margin: 12px 0;
}

.score {
  font-size: 14px;
  color: #888;
  margin: 8px 0;
}

.btn-download,
.btn-link {
  display: inline-block;
  padding: 10px 16px;
  background: #1976d2;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  margin-top: 12px;
  transition: background 0.2s;
}

.btn-download:hover,
.btn-link:hover {
  background: #1565c0;
}

.btn-link {
  background: #4caf50;
}

.btn-link:hover {
  background: #45a049;
}

.file-size {
  opacity: 0.8;
  font-size: 12px;
  margin-left: 4px;
}

.error {
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  margin: 16px 0;
}
```

---

## 🔄 4. Vue.js

### Composable

```javascript
// composables/useUVGAgent.js
import { ref } from 'vue';

export function useUVGAgent() {
  const loading = ref(false);
  const error = ref(null);
  const data = ref(null);
  
  async function ask(query, options = {}) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          size: options.size || 30,
          max_chunks: options.maxChunks || 20,
          use_semantic: options.useSemanctic !== false,
          min_score: options.minScore || 0.0
        })
      });
      
      const result = await response.json();
      data.value = result;
      return result;
      
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  return {
    ask,
    loading,
    error,
    data
  };
}
```

### Componente

```vue
<template>
  <div class="chat-interface">
    <form @submit.prevent="handleSubmit">
      <input
        v-model="query"
        type="text"
        placeholder="Pregunta sobre UVG..."
        :disabled="loading"
      />
      <button type="submit" :disabled="loading">
        {{ loading ? 'Buscando...' : 'Preguntar' }}
      </button>
    </form>
    
    <div v-if="error" class="error">
      ❌ Error: {{ error }}
    </div>
    
    <div v-if="data">
      <div class="answer">
        <h2>Respuesta</h2>
        <p>{{ data.answer }}</p>
      </div>
      
      <div class="sources">
        <h2>Fuentes ({{ data.sources.length }})</h2>
        <SourceItem
          v-for="(source, idx) in data.sources"
          :key="idx"
          :source="source"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUVGAgent } from '@/composables/useUVGAgent';
import SourceItem from './SourceItem.vue';

const query = ref('');
const { ask, loading, error, data } = useUVGAgent();

async function handleSubmit() {
  if (!query.value.trim()) return;
  await ask(query.value);
}
</script>
```

---

## 📱 5. Descarga Programática (Sin UI)

### Descargar archivo directamente en JS

```javascript
async function downloadFile(resourceId, fileId, filename) {
  try {
    const response = await fetch(`/download/${resourceId}/${fileId}`);
    
    if (!response.ok) {
      throw new Error('Error descargando archivo');
    }
    
    // Obtener blob
    const blob = await response.blob();
    
    // Crear URL temporal
    const url = window.URL.createObjectURL(blob);
    
    // Crear link temporal y hacer click
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Limpiar
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    console.log('✅ Archivo descargado:', filename);
    
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Uso
downloadFile(
  '2d65cc83db6d363db69217c482646c16',
  '2d65cc83db6d363db69217c482646c16',
  'Informatica.pdf'
);
```

### Abrir PDF en nueva pestaña

```javascript
function openPDFInNewTab(resourceId, fileId) {
  const url = `/download/${resourceId}/${fileId}`;
  window.open(url, '_blank');
}
```

### Previsualización de PDF con PDF.js

```javascript
async function previewPDF(resourceId, fileId, canvasId) {
  const url = `/download/${resourceId}/${fileId}`;
  
  // Cargar PDF.js
  const pdfjsLib = window['pdfjs-dist/build/pdf'];
  pdfjsLib.GlobalWorkerOptions.workerSrc = '//cdn.jsdelivr.net/npm/pdfjs-dist@2.9.359/build/pdf.worker.min.js';
  
  // Cargar documento
  const loadingTask = pdfjsLib.getDocument(url);
  const pdf = await loadingTask.promise;
  
  // Renderizar primera página
  const page = await pdf.getPage(1);
  const scale = 1.5;
  const viewport = page.getViewport({ scale });
  
  const canvas = document.getElementById(canvasId);
  const context = canvas.getContext('2d');
  canvas.height = viewport.height;
  canvas.width = viewport.width;
  
  await page.render({
    canvasContext: context,
    viewport: viewport
  }).promise;
  
  console.log('✅ PDF renderizado');
}
```

---

## 🧪 6. Testing

### Test con Jest

```javascript
import { askQuestion, downloadFile } from './api';

describe('UVG Agent API', () => {
  test('should return sources with downloadable files', async () => {
    const data = await askQuestion('CISCO academy');
    
    expect(data).toHaveProperty('answer');
    expect(data).toHaveProperty('sources');
    expect(Array.isArray(data.sources)).toBe(true);
    
    // Verificar que hay archivos descargables
    const downloadable = data.sources.filter(s => s.is_downloadable);
    expect(downloadable.length).toBeGreaterThan(0);
    
    // Verificar estructura de file
    downloadable.forEach(source => {
      expect(source.file).toHaveProperty('download_url');
      expect(source.file).toHaveProperty('content_type');
      expect(source.file).toHaveProperty('size');
      expect(source.file).toHaveProperty('filename');
      expect(source.file).toHaveProperty('file_id');
    });
  });
  
  test('should download file successfully', async () => {
    const blob = await downloadFile('resource-id', 'file-id');
    expect(blob).toBeInstanceOf(Blob);
    expect(blob.size).toBeGreaterThan(0);
  });
});
```

---

## 📦 7. Axios (Alternativa a Fetch)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

async function askQuestion(query) {
  try {
    const response = await api.post('/ask', {
      query,
      size: 30,
      max_chunks: 20,
      use_semantic: true,
      min_score: 0.0
    });
    
    return response.data;
    
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

async function downloadFile(resourceId, fileId) {
  try {
    const response = await api.get(`/download/${resourceId}/${fileId}`, {
      responseType: 'blob'
    });
    
    return response.data;
    
  } catch (error) {
    console.error('Error descargando:', error);
    throw error;
  }
}

export { askQuestion, downloadFile };
```

---

## 🎉 ¡Listo para Integrar!

Estos ejemplos cubren los casos de uso más comunes. Puedes adaptarlos a tu framework y necesidades específicas.

**Características implementadas:**
- ✅ Query con detección automática de archivos
- ✅ Descarga de PDFs, Excel y otros archivos
- ✅ Links externos
- ✅ Streaming eficiente
- ✅ Seguro (no expone API key)
