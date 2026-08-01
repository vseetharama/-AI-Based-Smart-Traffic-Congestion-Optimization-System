import { motion, useReducedMotion } from "framer-motion";

export default function AnimatedHeading({
  as = "h2",
  children,
  className = "",
  underline = true,
  shimmer = true,
  hero = false,
}) {
  const prefersReducedMotion = useReducedMotion();
  const Component = motion[as];

  const baseClassName = `${hero ? "relative inline-block" : "relative inline-block"} ${className}`;

  return (
    <div className="flex flex-col items-center text-center">
      <Component
        className={baseClassName}
        initial={prefersReducedMotion ? false : hero ? { opacity: 0, y: 18, scale: 0.95, filter: "blur(10px)" } : { opacity: 0, y: 18, filter: "blur(8px)" }}
        animate={hero && !prefersReducedMotion ? { opacity: 1, y: 0, scale: 1, filter: "blur(0px)" } : undefined}
        whileInView={hero ? undefined : prefersReducedMotion ? undefined : { opacity: 1, y: 0, filter: "blur(0px)" }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
        style={{ textShadow: "0 0 18px rgba(34, 211, 238, 0.16)" }}
      >
        {children}
        {shimmer && (
          <motion.span
            className="pointer-events-none absolute inset-0 rounded-full"
            initial={prefersReducedMotion ? false : { opacity: 0, x: "-120%" }}
            animate={hero && !prefersReducedMotion ? { opacity: [0, 0.4, 0], x: ["-120%", "220%"] } : undefined}
            whileInView={hero ? undefined : prefersReducedMotion ? undefined : { opacity: [0, 0.35, 0], x: ["-120%", "220%"] }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 1.15, ease: "easeInOut" }}
            style={{
              background: "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.38) 45%, transparent 100%)",
              transform: "skewX(-18deg)",
              mixBlendMode: "screen",
            }}
          />
        )}
      </Component>
      {underline && (
        <motion.span
          className="mt-3 block h-[2px] w-24 rounded-full bg-gradient-to-r from-cyan-400 via-sky-400 to-purple-500"
          initial={prefersReducedMotion ? false : { scaleX: 0, opacity: 0 }}
          animate={hero && !prefersReducedMotion ? { scaleX: 1, opacity: 1 } : undefined}
          whileInView={hero ? undefined : prefersReducedMotion ? undefined : { scaleX: 1, opacity: 1 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.55, ease: "easeOut" }}
          style={{ transformOrigin: "center" }}
        />
      )}
    </div>
  );
}
