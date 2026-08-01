import { motion, useReducedMotion } from "framer-motion";

export default function FeatureCard({ icon, title, description, accent, onLearnMore }) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      className="group relative h-full overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70 p-5 shadow-[0_10px_35px_rgba(2,8,23,0.28)] backdrop-blur-md transition duration-300 hover:border-cyan-400/30"
      whileHover={prefersReducedMotion ? undefined : { y: -6, scale: 1.01, boxShadow: "0 20px 45px rgba(34, 211, 238, 0.16)" }}
      transition={{ duration: 0.25 }}
    >
      <motion.div
        className="pointer-events-none absolute inset-0 rounded-2xl"
        whileHover={prefersReducedMotion ? undefined : { background: "radial-gradient(circle at var(--x, 20%) var(--y, 20%), rgba(34, 211, 238, 0.14), transparent 45%)" }}
      />
      <div className={`inline-flex rounded-2xl bg-gradient-to-br ${accent} p-3 text-2xl`}>
        {icon}
      </div>

      <h3 className="mt-4 text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>

      <motion.button
        type="button"
        onClick={onLearnMore}
        whileHover={prefersReducedMotion ? undefined : { scale: 1.03, boxShadow: "0 0 20px rgba(34, 211, 238, 0.18)" }}
        whileTap={prefersReducedMotion ? undefined : { scale: 0.97 }}
        className="mt-4 inline-flex items-center rounded-pill border border-cyan-400/20 bg-cyan-500/10 px-3 py-2 text-sm font-medium text-cyan-300 transition hover:bg-cyan-500/20"
      >
        <span>Learn more</span>
        <motion.span className="ml-2" whileHover={prefersReducedMotion ? undefined : { x: 4 }} transition={{ duration: 0.2 }}>
          →
        </motion.span>
      </motion.button>
    </motion.div>
  );
}
