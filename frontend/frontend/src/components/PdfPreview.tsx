// src/components/PdfPreview.tsx
import { useEffect, useState } from "react";
import { resourceFileUrl } from "../api";

/**
 * Renderiza un PDF embebido usando Blob URL.
 * Evita convertir el binario a texto (adiós "�����").
 */
export default function PdfPreview({ resourceId, height = "70vh" }: { resourceId: string; height?: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let objectUrl: string | null = null;

    (async () => {
      try {
        const res = await fetch(resourceFileUrl(resourceId));
        if (!res.ok) throw new Error(`No se pudo descargar el PDF (${res.status})`);
        const buf = await res.arrayBuffer();
        const blob = new Blob([buf], { type: "application/pdf" });
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      } catch (e: any) {
        setError(e?.message || "Error cargando PDF");
      }
    })();

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [resourceId]);

  if (error) {
    return <div className="rounded-lg border border-red-500/40 bg-red-900/20 p-3 text-sm text-red-200">⚠️ {error}</div>;
  }

  if (!url) {
    return <div className="rounded-lg border border-white/10 bg-white/5 p-3 text-sm text-white/80">Cargando PDF…</div>;
  }

  return (
    <iframe
      src={url}
      title="Vista previa PDF"
      style={{ width: "100%", height, border: "none", borderRadius: 12 }}
    />
  );
}

