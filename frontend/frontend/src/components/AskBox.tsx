import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

type Props = {
  onAsk: (q: string) => void;        // 👈 ya no enviamos endpoint
  loading: boolean;
  variant?: "composer" | "panel";
};

export default function AskBox({
  onAsk,
  loading,
  variant = "composer",
}: Props) {
  const [q, setQ] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    // autosize básico
    const el = textareaRef.current;
    if (!el) return;
    const handler = () => {
      el.style.height = "0px";
      el.style.height = Math.min(160, el.scrollHeight) + "px";
    };
    handler();
    el.addEventListener("input", handler);
    return () => el.removeEventListener("input", handler);
  }, []);

  const send = () => {
    if (!q.trim() || loading) return;
    onAsk(q.trim());
    setQ("");
    textareaRef.current?.focus();
  };

  return (
    <div
      className={[
        "rounded-2xl border border-white/10 bg-white/5 backdrop-blur",
        variant === "composer" ? "px-3 py-2" : "p-3",
      ].join(" ")}
    >
      <div className="flex items-end gap-2">
        {/* input */}
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            rows={1}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Escribe tu pregunta…"
            className="w-full resize-none bg-transparent outline-none text-white placeholder-white/40 px-4 py-3"
            aria-label="Escribe tu pregunta"
          />
        </div>

        {/* enviar */}
        <motion.button
          whileTap={{ scale: 0.98 }}
          whileHover={!loading && q.trim() ? { scale: 1.02 } : {}}
          onClick={send}
          disabled={!q.trim() || loading}
          className={`shrink-0 inline-flex items-center justify-center rounded-xl px-5 py-3 font-medium transition ${
            !q.trim() || loading
              ? "bg-white/10 text-white/40 cursor-not-allowed"
              : "bg-emerald-600 text-white hover:bg-emerald-700"
          }`}
          aria-label="Preguntar"
        >
          {loading ? "Enviando…" : "Preguntar"}
        </motion.button>
      </div>
    </div>
  );
}
