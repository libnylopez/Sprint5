import React from "react";
import type { SourceDoc } from "./SourceCard";
import SourceCard from "./SourceCard";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;           // puede venir con **negritas**, listas, etc.
  sources?: SourceDoc[];
};

export default function ChatMessage({ m }: { m: Message }) {
  const isAssistant = m.role === "assistant";

  return (
    <div className={`flex ${isAssistant ? "justify-start" : "justify-end"}`}>
      <div className="max-w-[85%]">
        <div
          className={[
            "rounded-2xl px-5 py-4 border backdrop-blur transition",
            isAssistant
              ? "bg-white/5 border-white/10"
              : "bg-emerald-600/15 border-emerald-500/20",
          ].join(" ")}
        >
          {/* Markdown bonito */}
          <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-li:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.text}</ReactMarkdown>
          </div>
        </div>

        {isAssistant && m.sources && m.sources.length > 0 && (
          <div className="mt-3 grid grid-cols-1 gap-3">
            {m.sources.map((s) => (
              <SourceCard key={s.id} s={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
