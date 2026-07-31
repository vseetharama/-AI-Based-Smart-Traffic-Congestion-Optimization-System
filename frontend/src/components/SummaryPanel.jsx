import InsightCard from "./InsightCard";

function SummaryPanel({ metrics, status, lastUpdated }) {
  const cards = [
    {
      title: "System Status",
      value: status === "RUNNING" ? "RUNNING" : "OFFLINE",
      icon: "🟢",
      subtitle: status === "RUNNING" ? "Live dashboard polling active" : "No fresh data received",
      tone: status === "RUNNING" ? "success" : "danger",
    },
    {
      title: "Current Active Road",
      value: metrics.activeRoad || "None",
      icon: "🛣️",
      subtitle: metrics.activeRoad ? "Current green road from the dashboard" : "Waiting for live data",
      tone: "default",
    },
    {
      title: "Current Signal Timer",
      value: metrics.currentTimer ? `${metrics.currentTimer} sec` : "0 sec",
      icon: "⏱️",
      subtitle: "Live timer from the current signal cycle",
      tone: "warning",
    },
    {
      title: "Highest Density",
      value: metrics.highestDensity || "NONE",
      icon: "📈",
      subtitle: metrics.highestDensity ? "Highest density detected among roads" : "No traffic detected",
      tone: metrics.highestDensity === "HIGH" ? "danger" : "default",
    },
    {
      title: "Total Vehicles",
      value: metrics.totalVehicles || "No traffic data available",
      icon: "🚗",
      subtitle: metrics.totalVehicles ? "Combined live vehicle count" : "All roads are idle",
      tone: metrics.totalVehicles ? "success" : "default",
    },
    {
      title: "Last Updated",
      value: lastUpdated || "Not available",
      icon: "🕒",
      subtitle: "Most recent dashboard timestamp",
      tone: "default",
    },
  ];

  return (
    <div className="row g-2 mb-3">
      {cards.map((card) => (
        <div key={card.title} className="col-12 col-md-6 col-xl-4">
          <InsightCard {...card} />
        </div>
      ))}
    </div>
  );
}

export default SummaryPanel;
