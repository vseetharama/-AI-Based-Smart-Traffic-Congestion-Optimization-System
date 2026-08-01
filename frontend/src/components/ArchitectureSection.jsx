import { useEffect, useRef, useState } from "react";
import AnimatedHeading from "./AnimatedHeading";

const steps = [
  {
    icon: "📤",
    title: "Upload Video",
    description: "Video input is submitted for analysis.",
    accent: "from-cyan-500/20 to-blue-500/20",
  },
  {
    icon: "🎥",
    title: "YOLO Vehicle Detection",
    description: "Vehicles are detected frame by frame.",
    accent: "from-sky-500/20 to-indigo-500/20",
  },
  {
    icon: "🚗",
    title: "Vehicle Counting",
    description: "Detected vehicles are counted and tracked.",
    accent: "from-violet-500/20 to-purple-500/20",
  },
  {
    icon: "📊",
    title: "Traffic Density Analysis",
    description: "The system evaluates congestion levels.",
    accent: "from-emerald-500/20 to-green-500/20",
  },
  {
    icon: "🚦",
    title: "Adaptive Signal Optimization",
    description: "Signal timing is adjusted dynamically.",
    accent: "from-amber-500/20 to-orange-500/20",
  },
  {
    icon: "🖥",
    title: "Live Dashboard",
    description: "Current traffic status is displayed instantly.",
    accent: "from-blue-500/20 to-cyan-500/20",
  },
  {
    icon: "☁️",
    title: "MongoDB Atlas Storage",
    description: "Results are persisted for later use.",
    accent: "from-fuchsia-500/20 to-pink-500/20",
  },
  {
    icon: "📈",
    title: "Historical Analytics",
    description: "Past traffic patterns are analyzed over time.",
    accent: "from-rose-500/20 to-red-500/20",
  },
  {
    icon: "📄",
    title: "PDF / CSV Report Generation",
    description: "Reports are exported for review and sharing.",
    accent: "from-teal-500/20 to-emerald-500/20",
  },
];

export default function ArchitectureSection() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const node = sectionRef.current;
    if (!node) return undefined;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="mt-10 md:mt-14">
      <div className="text-center">
        <AnimatedHeading as="h2" className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-2xl font-semibold text-transparent sm:text-3xl">
          System Architecture & Workflow
        </AnimatedHeading>
        <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
          The complete traffic-control pipeline from upload to reporting.
        </p>
      </div>

      <div className="mt-8">
        <div className="flex flex-wrap items-start justify-center gap-3 md:gap-4 lg:gap-3">
          {steps.map((step, index) => (
            <div key={step.title} className="flex w-full flex-col items-center md:w-[calc(50%-0.75rem)] lg:w-auto lg:flex-1">
              <div
                className={`flow-card ${isVisible ? "is-visible" : ""}`}
                style={{ animationDelay: `${index * 0.25}s` }}
              >
                <div className={`inline-flex rounded-2xl bg-gradient-to-br ${step.accent} p-3 text-2xl`}>
                  {step.icon}
                </div>
                <h3 className="mt-3 text-base font-semibold text-white">{step.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">{step.description}</p>
                <div className="flow-glow" />
              </div>

              {index < steps.length - 1 && (
                <>
                  <div className={`flow-connector hidden lg:flex ${isVisible ? "is-visible" : ""}`}>
                    <div className="flow-connector-line" />
                    <span className="flow-connector-icon">→</span>
                  </div>
                  <div className={`flow-connector flex flex-col items-center lg:hidden ${isVisible ? "is-visible" : ""}`}>
                    <div className="flow-connector-line vertical" />
                    <span className="flow-connector-icon">↓</span>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
