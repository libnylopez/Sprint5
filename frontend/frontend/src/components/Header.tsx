import React from "react";

export type BackendStatus = "online" | "offline" | "checking";

export default function Header({
  status,
  onNewChat,
}: {
  status: BackendStatus;
  onNewChat: () => void;
}) {
  const dot =
    status === "online"
      ? "bg-emerald-500"
      : status === "checking"
      ? "bg-amber-400"
      : "bg-rose-500";

  return (
    <div className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-black/20 bg-black/30 border-b border-white/10">
      <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
        {/* Izquierda: Nuevo chat */}
        <div className="flex items-center gap-2">
          <button
            onClick={onNewChat}
            className="rounded-xl bg-white/5 hover:bg-white/10 px-3 py-2 text-sm border border-white/10 transition"
            title="Limpiar conversación y comenzar de nuevo"
          >
            Nuevo chat
          </button>
        </div>

        {/* Derecha: estado backend */}
        <div className="flex items-center gap-2 text-sm text-white/70">
          <span className={`inline-flex h-2.5 w-2.5 rounded-full ${dot}`} />
          <span>Backend: {status[0].toUpperCase() + status.slice(1)}</span>
        </div>
      </div>
    </div>
  );
}
