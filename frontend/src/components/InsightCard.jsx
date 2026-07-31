function InsightCard({ title, value, icon, subtitle, tone = "default" }) {
  const tones = {
    default: { border: "rgba(255,255,255,0.08)", iconBg: "rgba(59,130,246,0.16)", iconColor: "#60a5fa" },
    success: { border: "rgba(74,222,128,0.18)", iconBg: "rgba(34,197,94,0.16)", iconColor: "#4ade80" },
    warning: { border: "rgba(250,204,21,0.18)", iconBg: "rgba(250,204,21,0.16)", iconColor: "#facc15" },
    danger: { border: "rgba(248,113,113,0.18)", iconBg: "rgba(248,113,113,0.16)", iconColor: "#f87171" },
  };

  const activeTone = tones[tone] || tones.default;

  return (
    <div className="card h-100" style={{ background: "rgba(10,14,24,0.94)", border: `1px solid ${activeTone.border}`, borderRadius: "18px", boxShadow: "0 10px 24px rgba(2, 8, 23, 0.28)" }}>
      <div className="card-body p-3 p-md-4">
        <div className="d-flex align-items-center gap-3">
          <div style={{ width: "44px", height: "44px", borderRadius: "12px", display: "grid", placeItems: "center", background: activeTone.iconBg, color: activeTone.iconColor, fontSize: "20px" }}>
            {icon}
          </div>
          <div className="min-w-0">
            <h6 className="mb-1 text-white fw-semibold" style={{ fontSize: "0.9rem" }}>{title}</h6>
            <div className="fw-bold text-white" style={{ fontSize: "1.02rem", lineHeight: 1.3 }}>{value}</div>
          </div>
        </div>
        {subtitle && <div className="mt-3" style={{ color: "#cbd5e1", fontSize: "0.84rem", lineHeight: 1.5 }}>{subtitle}</div>}
      </div>
    </div>
  );
}

export default InsightCard;
