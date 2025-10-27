// src/components/SourceCard.tsx
import React from "react";
import { motion } from "framer-motion";
import PdfPreview from "./PdfPreview";
import { resourceFileUrl } from "../api";

export type SourceDoc = {
  /** Usa aquí el ID de recurso de tu RAG/Nuclia para PDFs */
  id: string;
  title: string;
  url?: string;
  /** "pdf" para activar la vista embebida */
  type?: "pdf" | "link" | "file";
  snippet?: string;
};

export default function SourceCard({ s }: { s: SourceDoc }) {
  const isPdf = s.type === "pdf";
  const pdfUrl = isPdf ? resourceFileUrl(s.id) : undefined;

  const Icon = (
    <svg className="h-5 w-5 text-emerald-400" viewBox="0 0 24 24" fill="none" aria-hidden>
      {isPdf ? (
        <path d="M6 2h7l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" stroke="currentColor" strokeWidth="1.5" />
      ) : (
        <path d="M4 4h16v16H4z" stroke="currentColor" strokeWidth="1.5" />
      )}
    </svg>
  );

  // Tarjeta para PDFs con preview embebido
  if (isPdf) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="rounded-2xl border border-white/10 bg-white/5 p-4"
      >
        <div className="mb-3 flex items-center gap-2">
          {Icon}
          <div className="min-w-0">
            <div className="truncate font-medium text-white">{s.title}</div>
            {s.snippet && <div className="mt-1 text-sm text-white/70">{s.snippet}</div>}
          </div>
        </div>

        <PdfPreview resourceId={s.id} />

        <div className="mt-3 flex items-center gap-3 text-sm">
          <a
            href={pdfUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-emerald-500/40 bg-emerald-600/20 px-3 py-1.5 font-medium text-emerald-200 hover:bg-emerald-600/30"
          >
            Abrir PDF en pestaña nueva
          </a>
          {s.url && (
            <a
              href={s.url}
              target="_blank"
              rel="noreferrer"
              className="rounded-lg border border-white/10 bg-white/10 px-3 py-1.5 text-white/80 hover:bg-white/20"
            >
              Ver recurso en origen
            </a>
          )}
        </div>
      </motion.div>
    );
  }

  // Tarjeta genérica (links/otros)
  return (
    <motion.a
      href={s.url || "#"}
      target={s.url ? "_blank" : undefined}
      rel={s.url ? "noreferrer" : undefined}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="group block rounded-2xl border border-white/10 bg-white/5 p-4"
    >
      <div className="flex items-start gap-2">
        {Icon}
        <div className="min-w-0">
          <div className="truncate font-medium text-white group-hover:text-emerald-300">
            {s.title}
          </div>
          {s.snippet && (
            <div className="mt-1 max-h-12 overflow-hidden text-sm text-white/70">
              {s.snippet}
            </div>
          )}
        </div>
      </div>
    </motion.a>
  );
}
