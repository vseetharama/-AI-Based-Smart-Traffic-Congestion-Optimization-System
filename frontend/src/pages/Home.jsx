import { useState } from "react";
import { Link } from "react-router-dom";
import { motion, useReducedMotion } from "framer-motion";
import Layout from "../components/Layout";
import OverviewSection from "../components/OverviewSection";
import TechnologyStack from "../components/TechnologyStack";
import ArchitectureSection from "../components/ArchitectureSection";
import FeatureCard from "../components/FeatureCard";
import ModalFeature from "../components/ModalFeature";
import AnimatedHeading from "../components/AnimatedHeading";

export default function Home() {
  const [activeFeature, setActiveFeature] = useState(null);
  const prefersReducedMotion = useReducedMotion();

  const features = [
    {
      icon: "🚗",
      title: "Vehicle Detection",
      tagline: "YOLOv8-powered perception",
      description: "Detects vehicles from uploaded traffic videos using the YOLOv8 object detection model.",
      overview: "The system identifies vehicles across video frames to build a reliable understanding of road activity.",
      howItWorks: "Frames are processed in sequence, and the model detects vehicle objects with confidence scoring for each frame.",
      technologies: "YOLOv8, OpenCV, Python",
      benefits: "Improves counting accuracy and provides the foundation for real-time traffic analysis.",
      futureScope: "Can be extended with vehicle classification, speed estimation, and lane-level analytics.",
      accent: "from-cyan-500/20 to-blue-500/20",
    },
    {
      icon: "📊",
      title: "Traffic Analysis",
      tagline: "Density classification",
      description: "Analyzes vehicle density and classifies traffic conditions as LOW, MEDIUM, or HIGH.",
      overview: "Traffic flow is interpreted from detected vehicle counts and transformed into actionable density states.",
      howItWorks: "The system evaluates live counts against threshold rules to determine whether traffic is light, moderate, or heavy.",
      technologies: "Python, Flask, Rule-based logic",
      benefits: "Makes congestion understandable and supports intelligent signal decisions.",
      futureScope: "Can evolve into predictive congestion forecasting with historical pattern analysis.",
      accent: "from-emerald-500/20 to-green-500/20",
    },
    {
      icon: "🚦",
      title: "Adaptive Signal Control",
      tagline: "Dynamic optimization",
      description: "Dynamically adjusts traffic signal timings based on detected congestion levels.",
      overview: "Signal timing is updated in response to current road conditions to reduce queues and waiting time.",
      howItWorks: "The controller evaluates congestion levels and assigns recommended green times to each road.",
      technologies: "Flask, Python, Traffic controller logic",
      benefits: "Improves traffic flow efficiency and lowers unnecessary delays at intersections.",
      futureScope: "Can integrate machine learning and adaptive scheduling based on time-of-day traffic patterns.",
      accent: "from-amber-500/20 to-orange-500/20",
    },
    {
      icon: "📈",
      title: "Real-Time Dashboard",
      tagline: "Live monitoring",
      description: "Displays live road status, vehicle count, density, timers, and predictions.",
      overview: "The dashboard provides a live overview of the current traffic state at the intersection.",
      howItWorks: "Updated summaries are pulled from the backend and rendered immediately for each monitored road.",
      technologies: "React, Bootstrap, Recharts",
      benefits: "Helps operators monitor conditions quickly and make informed observations in real time.",
      futureScope: "Can include live alerts, map views, and multi-intersection coordination.",
      accent: "from-violet-500/20 to-purple-500/20",
    },
    {
      icon: "☁",
      title: "Historical Analytics",
      tagline: "MongoDB-backed insights",
      description: "Stores traffic records in MongoDB Atlas and provides historical insights.",
      overview: "Captured records are preserved for trend analysis and future reporting.",
      howItWorks: "Process outputs are stored in MongoDB and retrieved for historical summaries and comparison views.",
      technologies: "MongoDB Atlas, Flask, Python",
      benefits: "Enables long-term traffic studies and evidence-based optimization decisions.",
      futureScope: "Can support seasonal trend detection and predictive analytics dashboards.",
      accent: "from-fuchsia-500/20 to-pink-500/20",
    },
    {
      icon: "📄",
      title: "Report Generation",
      tagline: "PDF and CSV exports",
      description: "Exports traffic analytics and historical summaries as PDF and CSV reports.",
      overview: "The system can package traffic insights into export-ready documents for review and documentation.",
      howItWorks: "Historical and live results are aggregated and formatted into downloadable report files.",
      technologies: "Flask, PDF/CSV export logic",
      benefits: "Supports reporting, evaluation, and sharing of project outcomes with stakeholders.",
      futureScope: "Can expand to automated weekly reports and scheduled email delivery.",
      accent: "from-teal-500/20 to-emerald-500/20",
    },
  ];

  return (
    <Layout>
      <div className="w-full max-w-full">

      {/* HERO */}
      <motion.section
        className="py-3 text-center"
        initial={prefersReducedMotion ? false : { opacity: 0, y: 24 }}
        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="mx-auto max-w-4xl">
          <AnimatedHeading hero className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text sm:text-5xl lg:text-6xl">
            AI-Based Smart Traffic Congestion Optimization System
          </AnimatedHeading>
          <motion.p
            className="mx-auto mt-4 max-w-2xl text-base text-slate-400 sm:text-lg"
            initial={prefersReducedMotion ? false : { opacity: 0, y: 16 }}
            animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ delay: 0.24, duration: 0.45 }}
          >
            Smart traffic control using YOLO detection, adaptive signal optimization, and real-time analytics.
          </motion.p>
        </div>

        <motion.div
          className="mt-6 flex flex-wrap justify-center gap-3"
          initial={prefersReducedMotion ? false : { opacity: 0, y: 14 }}
          animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ delay: 0.34, duration: 0.45 }}
        >
          <motion.div whileHover={prefersReducedMotion ? undefined : { scale: 1.03, boxShadow: "0 0 22px rgba(168, 85, 247, 0.22)" }} whileTap={prefersReducedMotion ? undefined : { scale: 0.97 }}>
            <Link to="/dashboard" className="btn btn-primary rounded-pill px-4 py-2 shadow-lg shadow-purple-500/30">
              🚦 Live Dashboard
            </Link>
          </motion.div>
          <motion.div whileHover={prefersReducedMotion ? undefined : { scale: 1.03, boxShadow: "0 0 18px rgba(34, 211, 238, 0.16)" }} whileTap={prefersReducedMotion ? undefined : { scale: 0.97 }}>
            <Link to="/analytics" className="btn btn-outline-light rounded-pill px-4 py-2">
              📊 Analytics
            </Link>
          </motion.div>
          <motion.div whileHover={prefersReducedMotion ? undefined : { scale: 1.03, boxShadow: "0 0 18px rgba(34, 211, 238, 0.16)" }} whileTap={prefersReducedMotion ? undefined : { scale: 0.97 }}>
            <Link to="/upload" className="btn btn-outline-light rounded-pill px-4 py-2">
              📤 Upload Videos
            </Link>
          </motion.div>
          <motion.div whileHover={prefersReducedMotion ? undefined : { scale: 1.03, boxShadow: "0 0 18px rgba(191, 219, 254, 0.16)" }} whileTap={prefersReducedMotion ? undefined : { scale: 0.97 }}>
            <a href="https://github.com/vseetharama/AI-Traffic-Control-System" target="_blank" rel="noreferrer" className="btn btn-outline-secondary rounded-pill px-4 py-2">
              GitHub
            </a>
          </motion.div>
        </motion.div>
      </motion.section>

      <OverviewSection />
      <TechnologyStack />
      <ArchitectureSection />

      {/* FEATURES */}
      <section className="mt-10 md:mt-14">
        <div className="text-center">
          <AnimatedHeading className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-2xl font-semibold text-transparent sm:text-3xl">
            Core Features
          </AnimatedHeading>
          <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
            Powerful AI-driven capabilities that enable intelligent traffic monitoring and adaptive signal optimization.
          </p>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="h-full"
              initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
              whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.4, delay: index * 0.08 }}
            >
              <FeatureCard {...feature} onLearnMore={() => setActiveFeature(feature)} />
            </motion.div>
          ))}
        </div>
      </section>

      <motion.section
        className="mt-12 rounded-3xl border border-white/10 bg-slate-950/60 px-5 py-6 backdrop-blur-sm sm:px-8"
        initial={prefersReducedMotion ? false : { opacity: 0, y: 24 }}
        whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.45 }}
      >
        <div className="row align-items-center g-4">
          <div className="col-12 col-lg-8">
            <h3 className="text-xl font-semibold text-white">Built for final-year engineering demonstration</h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              The platform combines computer vision, adaptive control, analytics, and modern web interfaces into a complete capstone-style traffic management solution.
            </p>
          </div>
          <div className="col-12 col-lg-4 text-lg-end">
            <motion.div whileHover={prefersReducedMotion ? undefined : { scale: 1.03, boxShadow: "0 0 18px rgba(34, 211, 238, 0.18)" }} whileTap={prefersReducedMotion ? undefined : { scale: 0.97 }}>
              <Link to="/members" className="btn btn-outline-light rounded-pill px-4 py-2">
                Meet the Team
              </Link>
            </motion.div>
          </div>
        </div>
      </motion.section>

      <motion.footer
        className="mt-12 rounded-3xl border border-white/10 bg-slate-950/60 px-5 py-6 text-sm text-slate-400 backdrop-blur-sm sm:px-8"
        initial={prefersReducedMotion ? false : { opacity: 0, y: 24 }}
        whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.45 }}
      >
        <div className="row g-4">
          <div className="col-12 col-lg-4">
            <h4 className="mb-2 text-white">AI-Based Smart Traffic Congestion Optimization System</h4>
            <p className="mb-0">Developed by Team 05</p>
            <p className="mb-0">Department of Computer Science & Engineering</p>
          </div>
          <div className="col-12 col-sm-6 col-lg-4">
            <h5 className="mb-2 text-white">Powered by</h5>
            <div className="d-flex flex-wrap gap-2">
              {['React', 'Flask', 'YOLOv8', 'MongoDB Atlas'].map((item) => (
                <span key={item} className="rounded-pill border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">{item}</span>
              ))}
            </div>
          </div>
          <div className="col-12 col-sm-6 col-lg-4 text-sm-start text-lg-end">
            <p className="mb-1">Version 1.0</p>
            <p className="mb-0">© 2026 Team 05</p>
          </div>
        </div>
      </motion.footer>

      <ModalFeature isOpen={Boolean(activeFeature)} onClose={() => setActiveFeature(null)} feature={activeFeature} />

      </div>
    </Layout>
  );
}