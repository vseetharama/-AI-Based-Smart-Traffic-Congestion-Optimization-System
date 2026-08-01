import WorkflowStep from "./WorkflowStep";

const steps = [
  {
    stepNumber: "01",
    icon: "📤",
    title: "Upload Traffic Video",
    description: "Users upload video footage for one or more roads.",
    accent: "from-cyan-500/20 to-blue-500/20",
  },
  {
    stepNumber: "02",
    icon: "🎥",
    title: "YOLOv8 Vehicle Detection",
    description: "Vehicles are detected in every video frame.",
    accent: "from-sky-500/20 to-indigo-500/20",
  },
  {
    stepNumber: "03",
    icon: "🚗",
    title: "Vehicle Counting",
    description: "Detected vehicles are counted for each road.",
    accent: "from-violet-500/20 to-purple-500/20",
  },
  {
    stepNumber: "04",
    icon: "📊",
    title: "Traffic Density Analysis",
    description: "Traffic is classified as LOW, MEDIUM, or HIGH.",
    accent: "from-emerald-500/20 to-green-500/20",
  },
  {
    stepNumber: "05",
    icon: "🚦",
    title: "Adaptive Signal Optimization",
    description: "Signal timings are adjusted based on congestion.",
    accent: "from-amber-500/20 to-orange-500/20",
  },
  {
    stepNumber: "06",
    icon: "🖥",
    title: "Live Dashboard Update",
    description: "Road status, density, and timers are shown in real time.",
    accent: "from-blue-500/20 to-cyan-500/20",
  },
  {
    stepNumber: "07",
    icon: "☁️",
    title: "Historical Data Storage",
    description: "Traffic insights are stored in MongoDB Atlas.",
    accent: "from-fuchsia-500/20 to-pink-500/20",
  },
  {
    stepNumber: "08",
    icon: "📈",
    title: "Analytics & Report Generation",
    description: "Charts, PDF reports, and CSV exports are generated.",
    accent: "from-teal-500/20 to-emerald-500/20",
  },
];

export default function WorkflowTimeline() {
  return (
    <section className="mt-10 md:mt-14">
      <div className="text-center">
        <h2 className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-2xl font-semibold text-transparent sm:text-3xl">
          Workflow
        </h2>
        <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
          Operational lifecycle of the AI-powered traffic management system.
        </p>
      </div>

      <div className="mt-6">
        <div className="hidden lg:block">
          <div className="flex items-start justify-between gap-3">
            {steps.map((step, index) => (
              <div key={step.title} className="flex-1">
                <WorkflowStep {...step} />
                {index < steps.length - 1 && (
                  <div className="mt-3 flex justify-center">
                    <div className="h-8 w-8 rounded-full border border-cyan-400/30 bg-cyan-500/10 text-center text-sm leading-8 text-cyan-300">
                      →
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="block lg:hidden">
          <div className="mx-auto max-w-2xl space-y-4">
            {steps.map((step, index) => (
              <div key={step.title} className="relative">
                <WorkflowStep {...step} />
                {index < steps.length - 1 && (
                  <div className="flex justify-center py-2">
                    <div className="h-6 w-6 rounded-full border border-cyan-400/30 bg-cyan-500/10 text-center text-xs leading-6 text-cyan-300">
                      ↓
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
