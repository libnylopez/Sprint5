import React from "react";
import { motion } from "framer-motion";

export default function Background() {
  return (
    <div className="fixed inset-0 -z-50 overflow-hidden">
      {/* base */}
      <div className="absolute inset-0 bg-[#0b0f0d]" />

      {/* grid tenue */}
      <div
        className="absolute inset-0 opacity-[0.05] pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* glow principal con movimiento */}
      <motion.div
        className="absolute -top-24 left-1/2 -translate-x-1/2 h-[720px] w-[1200px] rounded-full blur-3xl opacity-35"
        style={{
          background:
            "radial-gradient(60% 60% at 50% 40%, rgba(0,148,68,0.35) 0%, rgba(131,188,65,0.22) 35%, rgba(0,0,0,0) 70%)",
        }}
        animate={{ y: [0, 12, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* glow lateral */}
      <motion.div
        className="absolute bottom-[-120px] right-[-80px] h-[520px] w-[520px] rounded-full blur-3xl opacity-30"
        style={{
          background:
            "radial-gradient(50% 50% at 50% 50%, rgba(57,178,74,0.35) 0%, rgba(0,0,0,0) 70%)",
        }}
        animate={{ x: [0, -30, 0], y: [0, -10, 0] }}
        transition={{ duration: 24, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}
