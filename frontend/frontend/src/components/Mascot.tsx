import React, { memo } from "react";
import { motion } from "framer-motion";

type Props = {
  src: string;
  side?: "left" | "right";
  /** landing: centrado en el flujo; fixed: flotante en esquina */
  layout?: "landing" | "fixed";
  size?: "sm" | "md" | "lg";
};

/** Mascota con dos modos: landing (centrada, grande) y fixed (flotante lateral) */
function MascotBase({
  src,
  side = "right",
  layout = "fixed",
  size = "md",
}: Props) {
  const sizeCls =
    size === "lg"
      ? "h-56 w-56 md:h-72 md:w-72"
      : size === "sm"
      ? "h-32 w-32"
      : "h-44 w-44";

  if (layout === "landing") {
    return (
      <div className="relative mx-auto mt-6 md:mt-8 w-auto pointer-events-none">
        <div className="relative flex items-center justify-center">
          {/* halo */}
          <div
            className="absolute -inset-8 rounded-full blur-2xl opacity-40"
            style={{
              background:
                "radial-gradient(45% 45% at 50% 50%, rgba(0,148,68,0.5) 0%, rgba(0,0,0,0) 70%)",
            }}
          />
          <motion.img
            src={src}
            alt="Jack (mascota UVG)"
            className={`relative ${sizeCls} object-contain drop-shadow-[0_4px_40px_rgba(0,255,170,0.15)]`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, y: [0, -10, 0], rotate: [0, -1.5, 0] }}
            transition={{
              opacity: { duration: 0.8, ease: "easeOut" },
              y: { duration: 7, repeat: Infinity, ease: "easeInOut" },
              rotate: { duration: 7, repeat: Infinity, ease: "easeInOut" },
            }}
          />
        </div>
      </div>
    );
  }

  // layout fixed (flotante lateral)
  return (
    <div
      className={`pointer-events-none hidden md:block fixed top-28 ${
        side === "right" ? "right-6 lg:right-12" : "left-6 lg:left-12"
      } z-10`}
    >
      <div className="relative">
        <div
          className="absolute -inset-6 rounded-full blur-2xl opacity-40"
          style={{
            background:
              "radial-gradient(45% 45% at 50% 50%, rgba(0,148,68,0.5) 0%, rgba(0,0,0,0) 70%)",
          }}
        />
        <motion.img
          src={src}
          alt="Jack (mascota UVG)"
          className={`relative ${sizeCls} object-contain drop-shadow-[0_4px_40px_rgba(0,255,170,0.15)]`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: [0, -8, 0], rotate: [0, -1.5, 0] }}
          transition={{
            opacity: { duration: 0.8, ease: "easeOut" },
            y: { duration: 6, repeat: Infinity, ease: "easeInOut" },
            rotate: { duration: 6, repeat: Infinity, ease: "easeInOut" },
          }}
        />
      </div>
    </div>
  );
}

export default memo(MascotBase);
