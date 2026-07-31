function StatusBanner({ type = "info", title, message, children }) {
  const baseStyle = {
    borderRadius: "16px",
    padding: "16px 20px",
    marginTop: "20px",
    marginBottom: "10px",
    border: "1px solid rgba(255,255,255,0.12)",
    background: "rgba(255,255,255,0.05)",
    color: "#f8fafc",
    textAlign: "left",
  };

  const typeStyles = {
    success: { borderColor: "rgba(34, 197, 94, 0.35)", background: "rgba(34, 197, 94, 0.12)" },
    error: { borderColor: "rgba(248, 113, 113, 0.35)", background: "rgba(248, 113, 113, 0.12)" },
    info: { borderColor: "rgba(59, 130, 246, 0.35)", background: "rgba(59, 130, 246, 0.12)" },
  };

  const iconMap = {
    success: "✅",
    error: "⚠️",
    info: "ℹ️",
  };

  return (
    <div style={{ ...baseStyle, ...(typeStyles[type] || typeStyles.info) }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: title || message ? "8px" : "0" }}>
        <span>{iconMap[type] || iconMap.info}</span>
        {title && <strong>{title}</strong>}
      </div>
      {message && <div style={{ color: "#e2e8f0" }}>{message}</div>}
      {children}
    </div>
  );
}

export default StatusBanner;
