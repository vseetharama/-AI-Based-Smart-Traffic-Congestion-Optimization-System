import { motion, useReducedMotion } from "framer-motion";
import AnimatedHeading from "./AnimatedHeading";

const highlights = [
  { title: "Project Description", text: "A full-stack capstone system for intelligent traffic monitoring and signal control." },
  { title: "Objective", text: "Reduce congestion through AI-driven detection, analysis, and adaptive signal optimization." },
  { title: "Technologies Used", text: "React, Flask, YOLOv8, OpenCV, MongoDB Atlas, and Recharts." },
  { title: "Benefits", text: "Improves visibility, response time, and data-driven traffic management decisions." },
];

export default function OverviewSection() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.section
      className="mt-10 md:mt-14"
      initial={prefersReducedMotion ? false : { opacity: 0, y: 24 }}
      whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.45 }}
    >
      <div className="rounded-3xl border border-white/10 bg-slate-950/60 px-5 py-6 backdrop-blur-sm sm:px-8">
        <motion.div initial={prefersReducedMotion ? false : { opacity: 0, y: 16 }} whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.2 }} transition={{ duration: 0.45 }}>
          <AnimatedHeading as="h2" className="text-2xl font-semibold text-white">
            About the Project
          </AnimatedHeading>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400 sm:text-base">
            This project demonstrates an end-to-end smart traffic management system that combines computer vision, adaptive control, analytics, and a modern web dashboard for real-world traffic monitoring.
          </p>

          <div className="mt-5 row g-3">
            {highlights.map((item, index) => (
              <motion.div
                key={item.title}
                className="col-12 col-md-6 col-xl-3"
                initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
                whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <motion.div
                  whileHover={prefersReducedMotion ? undefined : { y: -6, boxShadow: "0 20px 45px rgba(34, 211, 238, 0.16)" }}
                  className="h-full rounded-2xl border border-white/10 bg-white/5 p-4 transition duration-300 hover:border-cyan-400/30"
                >
                  <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-400">{item.text}</p>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
}
