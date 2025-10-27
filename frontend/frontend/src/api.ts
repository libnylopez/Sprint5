// src/api.ts
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function ask(path: "/ask" | "/ask-nuclia", question: string) {
  const body = {
    query: question,
    size: 30,
    max_chunks: 10,
    use_semantic: true,
    min_score: 0.0,
  };
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    // intenta leer detalle JSON del backend
    const err = await res.json().catch(() => ({}));
    throw new Error((err as any)?.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function health(): Promise<boolean> {
  try {
    const r = await fetch(`${API_BASE}/health`);
    return r.ok;
  } catch {
    return false;
  }
}

/** URL del archivo original proxyeado por el backend (PDF u otros) */
export function resourceFileUrl(resourceId: string) {
  return `${API_BASE}/resources/${resourceId}/file`;
}
