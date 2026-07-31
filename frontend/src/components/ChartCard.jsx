function ChartCard({ title, subtitle, children }) {
  return (
    <div className="card h-100" style={{ background: "rgba(10,14,24,0.9)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "18px" }}>
      <div className="card-body p-4">
        <div className="mb-3">
          <h5 className="text-white mb-1">{title}</h5>
          {subtitle && <div className="text-muted small">{subtitle}</div>}
        </div>
        {children}
      </div>
    </div>
  );
}

export default ChartCard;
