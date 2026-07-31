function InsightCard({ title, value, icon, subtitle, tone = "default" }) {
  const tones = {
    default: { border: "rgba(255,255,255,0.08)", iconBg: "rgba(59,130,246,0.16)", iconColor: "#60a5fa" },
    success: { border: "rgba(74,222,128,0.18)", iconBg: "rgba(34,197,94,0.16)", iconColor: "#4ade80" },
    warning: { border: "rgba(250,204,21,0.18)", iconBg: "rgba(250,204,21,0.16)", iconColor: "#facc15" },
    danger: { border: "rgba(248,113,113,0.18)", iconBg: "rgba(248,113,113,0.16)", iconColor: "#f87171" },
  };

  const activeTone = tones[tone] || tones.default;

  return (
    <div className="card h-100" style={{ background: "rgba(10,14,24,0.9)", border: `1px solid ${activeTone.border}`, borderRadius: "18px" }}>
      <div className="card-body p-4">
        <div className="d-flex align-items-center gap-3">
          <div style={{ width: "44px", height: "44px", borderRadius: "12px", display: "grid", placeItems: "center", background: activeTone.iconBg, color: activeTone.iconColor, fontSize: "20px" }}>
            {icon}
          </div>
          <div>
            <h6 className="mb-1 text-slate-300" style={{ fontSize: "0.9rem" }}>{title}</h6>
            <div className="fw-bold text-white" style={{ fontSize: "1.05rem" }}>{value}</div>
          </div>
        </div>
        {subtitle && <div className="mt-3 text-muted small">{subtitle}</div>}
      </div>
    </div>
  );
}

export default InsightCard;
