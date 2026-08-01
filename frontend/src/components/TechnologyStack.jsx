import { motion, useReducedMotion } from "framer-motion";
import AnimatedHeading from "./AnimatedHeading";

const stacks = [
  {
    icon: "🖥",
    title: "Frontend",
    technologies: ["React", "Bootstrap", "Vite"],
  },
  {
    icon: "⚙️",
    title: "Backend",
    technologies: ["Python", "Flask"],
  },
  {
    icon: "🤖",
    title: "AI & Vision",
    technologies: ["YOLOv8", "OpenCV"],
  },
  {
    icon: "🗄️",
    title: "Database",
    technologies: ["MongoDB Atlas"],
  },
  {
    icon: "📈",
    title: "Analytics",
    technologies: ["Recharts"],
  },
  {
    icon: "📄",
    title: "Reports",
    technologies: ["PDF Export", "CSV Export"],
  },
];

export default function TechnologyStack() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.section
      className="mt-10 md:mt-14"
      initial={prefersReducedMotion ? false : { opacity: 0, y: 24 }}
      whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.45 }}
    >
      <div className="text-center">
        <AnimatedHeading as="h2" className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-2xl font-semibold text-transparent sm:text-3xl">
          Technology Stack
        </AnimatedHeading>
        <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
          Built using modern technologies for AI-powered traffic monitoring, analytics, and adaptive signal optimization.
        </p>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stacks.map((stack, index) => (
          <motion.div
            key={stack.title}
            className="rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-[0_10px_35px_rgba(2,8,23,0.28)] backdrop-blur-md transition duration-300 hover:-translate-y-1 hover:border-cyan-400/30"
            initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
            whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.4, delay: index * 0.08 }}
            whileHover={prefersReducedMotion ? undefined : { y: -6, scale: 1.01, boxShadow: "0 20px 45px rgba(34, 211, 238, 0.16)" }}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{stack.icon}</span>
              <h3 className="text-base font-semibold text-white">{stack.title}</h3>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {stack.technologies.map((tech) => (
                <span key={tech} className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] font-medium text-slate-300">
                  {tech}
                </span>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.section>
  );
}
