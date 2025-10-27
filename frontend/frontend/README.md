# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

---

## 🧠 Requisitos

- 🐍 Python **3.10+**
- 🧰 Node.js **18+** y **npm**
- 🐳 (opcional) Docker si usas **NucliaDB local**
- 🔑 API keys:
  - `ANTHROPIC_KEY` (Claude)
  - `NUCLIA_TOKEN`, `NUCLIA_API_BASE`, `KB` (Nuclia)

---

## ⚙️ Configuración del backend (FastAPI)

### 1️⃣ Ir al directorio del backend
```bash
cd UVG-Agent

2️⃣ Crear entorno virtual
python -m venv .venv

3️⃣ Activar entorno
.\.venv\Scripts\Activate.ps1

4️⃣ Instalar dependencias
pip install -r requirements.txt

5️⃣ Crear archivo .env
FRONT_ORIGIN=http://localhost:5173,http://127.0.0.1:5173
NUCLIA_API_BASE=https://api.nuclia.cloud/api/v1
KB=<id_de_tu_base_de_conocimiento>
NUCLIA_TOKEN=<tu_token_de_nuclia>
ANTHROPIC_KEY=<tu_api_key_de_anthropic>
CLAUDE_MODEL=claude-sonnet-4-20250514

6️⃣ Levantar el servidor
$env:FRONT_ORIGIN = "http://localhost:5173,http://127.0.0.1:5173"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

7️⃣ Probar

Docs (Swagger): http://localhost:8000/docs

Health Check: http://localhost:8000/health

💻 Configuración del frontend
1️⃣ Ir al directorio del frontend
cd frontend

2️⃣ Instalar dependencias
npm install

3️⃣ Crear archivo .env
VITE_API_BASE=http://localhost:8000
VITE_API_KEY=

4️⃣ Ejecutar el frontend
npm run dev


🌐 Abre http://localhost:5173

El texto “Backend: Online” aparecerá cuando la conexión con FastAPI sea exitosa.

🔄 Conexión Front ↔ Backend

El frontend se comunica mediante src/api.ts con:

POST /ask
{
  "query": "¿Cuáles son los requisitos de inscripción?",
  "size": 30,
  "max_chunks": 10,
  "use_semantic": true,
  "min_score": 0.0
}


Ejemplo de respuesta:

{
  "answer": "Para inscribirte debes llenar la solicitud en línea...",
  "sources": [
    {
      "title": "Guía de inscripción UVG Altiplano",
      "url": "https://uvg.edu.gt/altiplano/admisiones"
    }
  ]
}