import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Background from "./components/Background";
import Header, { BackendStatus } from "./components/Header";
import AskBox from "./components/AskBox";
import ChatMessage, { Message } from "./components/ChatMessage";
import type { SourceDoc } from "./components/SourceCard";
import Mascot from "./components/Mascot";
import TypingDots from "./components/TypingDots";
import { ask as askApi, health } from "./api";

const UVG_COLORS = { primary: "#056545" };
const mascotSrc = new URL("./assets/jack.png", import.meta.url).toString();

export default function App() {
  const [status, setStatus] = useState<BackendStatus>("offline");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  // autoscroll al final
  const bottomRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // medir altura del composer para padding dinámico
  const composerRef = useRef<HTMLDivElement | null>(null);
  const [composerH, setComposerH] = useState(160);
  useEffect(() => {
    if (!composerRef.current) return;
    const ro = new (window as any).ResizeObserver((entries: any) => {
      const h = entries[0]?.contentRect?.height ?? 160;
      setComposerH(h + 16);
    });
    ro.observe(composerRef.current);
    return () => ro.disconnect();
  }, []);

  // health (real)
  useEffect(() => {
    let dead = false;

    async function check() {
      try {
        setStatus("checking");
        const ok = await health();
        if (!dead) setStatus(ok ? "online" : "offline");
      } catch {
        if (!dead) setStatus("offline");
      }
    }

    check(); // al cargar
    const id = setInterval(check, 15000); // cada 15s (opcional)

    return () => {
      dead = true;
      clearInterval(id);
    };
  }, []);

  // enviar pregunta
  const onAsk = async (q: string) => {
    if (!q) return;
    setLoading(true);

    const user: Message = { id: crypto.randomUUID(), role: "user", text: q };
    setMessages((prev) => [...prev, user]);

    try {
      // Backend real
      const res = await askApi("/ask", q);

      const assistant: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: res?.answer ?? res?.reply ?? res?.content ?? "",
        sources: (res?.sources ?? []).map((s: any, i: number) => ({
          id: String(s.id ?? i),
          title: String(s.title ?? "Fuente"),
          url: s.url ?? undefined,
          type: String(s.url || "").toLowerCase().endsWith(".pdf")
            ? "pdf"
            : "link",
          snippet: s.text ?? s.snippet ?? undefined,
        })),
      };

      setMessages((p) => [...p, assistant]);
    } catch (e: any) {
      setMessages((p) => [
        ...p,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text:
            "Hubo un problema consultando el backend.\n\n```" +
            String(e?.message || e) +
            "```",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Nuevo chat: limpia la conversación
  const newChat = () => {
    setMessages([]);
  };

  const showLanding = messages.length === 0;
  const sealBottom = showLanding ? 24 : composerH + 8;

  return (
    <div className="min-h-screen antialiased text-white selection:bg-emerald-200/40 selection:text-emerald-900">
      <Background />
      <Header status={status} onNewChat={newChat} />

      <main
        className="mx-auto max-w-5xl px-4"
        style={{ paddingBottom: showLanding ? 32 : composerH }}
      >
        <AnimatePresence mode="wait">
          {showLanding ? (
            <motion.section
              key="landing"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="pt-12 md:pt-16 pb-4 text-center"
            >
              <motion.h1
                className="text-5xl md:text-7xl font-semibold tracking-tight"
                initial={{ letterSpacing: "-0.02em" }}
              >
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-white">
                  Jack
                </span>{" "}
                AI
              </motion.h1>

              {/* Mascota grande debajo */}
              <Mascot src={mascotSrc} layout="landing" size="lg" />

              {/* Input centrado */}
              <div className="mx-auto max-w-3xl mt-6 md:mt-8">
                <AskBox onAsk={onAsk} loading={loading} variant="panel" />
              </div>
            </motion.section>
          ) : (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="pt-4"
            >
              {/* Jack flotante lateral */}
              <Mascot src={mascotSrc} side="right" layout="fixed" size="md" />

              {/* Hilo de chat */}
              <div className="grid gap-4 md:gap-6">
                {messages.map((m) => (
                  <ChatMessage key={m.id} m={m} />
                ))}
                {loading && (
                  <div className="w-full flex justify-start">
                    <div className="max-w-[720px] w-full rounded-2xl border border-white/10 bg-white/5 px-5 py-4">
                      <TypingDots />
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Sello fijo abajo-izquierda */}
        <div
          className="fixed left-4 z-20 text-xs md:text-sm text-white/60 select-none"
          style={{ bottom: sealBottom }}
        >
          <span className="font-semibold tracking-wide">UVG Altiplano</span>
        </div>
      </main>

      {/* Composer fijo solo en modo chat */}
      {!showLanding && (
        <div ref={composerRef} className="fixed inset-x-0 bottom-0 z-30">
          <div className="mx-auto max-w-5xl px-4 pb-[max(0px,env(safe-area-inset-bottom))] pt-3">
            <AskBox onAsk={onAsk} loading={loading} variant="composer" />
            <div className="pointer-events-none -mt-5 mb-2 h-8 bg-gradient-to-t from-black/50 to-transparent rounded-t-2xl" />
          </div>
        </div>
      )}
    </div>
  );
}
