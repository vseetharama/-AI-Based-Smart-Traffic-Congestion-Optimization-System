export default function ArchitectureCard({ icon, title, description, accent }) {
  return (
    <div className="group h-full rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-[0_10px_35px_rgba(2,8,23,0.28)] backdrop-blur-md transition duration-300 hover:-translate-y-1 hover:border-cyan-400/30">
      <div className={`inline-flex rounded-2xl bg-gradient-to-br ${accent} p-2.5 text-xl`}>{icon}</div>
      <h3 className="mt-3 text-base font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>
    </div>
  );
}
