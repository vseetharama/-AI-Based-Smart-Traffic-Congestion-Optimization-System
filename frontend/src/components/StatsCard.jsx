function StatsCard({ title, value, icon, subtitle, tone = "default" }) {
  const tones = {
    default: {
      iconBg: "rgba(59, 130, 246, 0.16)",
      iconColor: "#60a5fa",
      border: "rgba(255,255,255,0.08)",
    },
    success: {
      iconBg: "rgba(34, 197, 94, 0.16)",
      iconColor: "#4ade80",
      border: "rgba(74, 222, 128, 0.18)",
    },
    warning: {
      iconBg: "rgba(250, 204, 21, 0.16)",
      iconColor: "#facc15",
      border: "rgba(250, 204, 21, 0.18)",
    },
    danger: {
      iconBg: "rgba(248, 113, 113, 0.16)",
      iconColor: "#f87171",
      border: "rgba(248, 113, 113, 0.18)",
    },
  };

  const selectedTone = tones[tone] || tones.default;

  return (
    <div
      className="card"
      style={{
        background: "rgba(10, 14, 24, 0.85)",
        border: `1px solid ${selectedTone.border}`,
        borderRadius: "18px",
        boxShadow: "0 15px 35px rgba(0, 0, 0, 0.22)",
        color: "#f8fafc",
      }}
    >
      <div className="card-body" style={{ padding: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "44px",
              height: "44px",
              borderRadius: "12px",
              display: "grid",
              placeItems: "center",
              fontSize: "20px",
              background: selectedTone.iconBg,
              color: selectedTone.iconColor,
            }}
          >
            {icon}
          </div>
          <div style={{ minWidth: 0 }}>
            <h6 style={{ margin: 0, fontSize: "0.9rem", color: "#cbd5e1" }}>{title}</h6>
            <div style={{ marginTop: "6px", fontSize: "1.1rem", fontWeight: 700, color: "#f8fafc" }}>
              {value}
            </div>
            {subtitle && (
              <small style={{ color: "#94a3b8", display: "block", marginTop: "4px" }}>{subtitle}</small>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatsCard;
