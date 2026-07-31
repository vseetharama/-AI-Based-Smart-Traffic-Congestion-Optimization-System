import InsightCard from "./InsightCard";

function InsightsPanel({ metrics }) {
  const cards = [
    {
      title: "Total Vehicles Detected",
      value: metrics.totalVehicles || "No traffic data available",
      icon: "🚗",
      subtitle: metrics.totalVehicles ? "Live sum from all roads" : "No vehicles currently detected",
      tone: metrics.totalVehicles ? "success" : "default",
    },
    {
      title: "Average Vehicles per Road",
      value: metrics.averageVehicles || "0.0",
      icon: "📊",
      subtitle: metrics.averageVehicles ? "Average per monitored road" : "No traffic data available",
      tone: "default",
    },
    {
      title: "Highest Traffic Road",
      value: metrics.highestTrafficRoad || "None",
      icon: "🏁",
      subtitle: metrics.highestTrafficRoad ? "Road with the most vehicles" : "No traffic detected",
      tone: "warning",
    },
    {
      title: "Least Busy Road",
      value: metrics.leastBusyRoad || "None",
      icon: "🌿",
      subtitle: metrics.leastBusyRoad ? "Road with the fewest vehicles" : "No traffic detected",
      tone: "default",
    },
    {
      title: "Highest Density",
      value: metrics.highestDensity || "NONE",
      icon: "📈",
      subtitle: metrics.highestDensity ? "Current peak density level" : "No traffic detected",
      tone: metrics.highestDensity === "HIGH" ? "danger" : "default",
    },
    {
      title: "Current Active Road",
      value: metrics.activeRoad || "None",
      icon: "🚦",
      subtitle: metrics.activeRoad ? "Live active green-road" : "No active road",
      tone: "default",
    },
    {
      title: "Current Green Timer",
      value: metrics.currentTimer ? `${metrics.currentTimer} sec` : "0 sec",
      icon: "⏱️",
      subtitle: "Live timer from the active signal",
      tone: "warning",
    },
    {
      title: "Roads Being Monitored",
      value: metrics.roadCount || 0,
      icon: "🧭",
      subtitle: "Number of road summaries in the dashboard",
      tone: "default",
    },
    {
      title: "System Running Status",
      value: metrics.systemStatus || "OFFLINE",
      icon: "⚙️",
      subtitle: metrics.systemStatus === "RUNNING" ? "Polling is active" : "Polling not available",
      tone: metrics.systemStatus === "RUNNING" ? "success" : "danger",
    },
    {
      title: "Last Dashboard Update Time",
      value: metrics.lastUpdated || "Not available",
      icon: "🕒",
      subtitle: "Newest received dashboard timestamp",
      tone: "default",
    },
  ];

  return (
    <div className="row g-2 mb-3">
      {cards.map((card) => (
        <div key={card.title} className="col-12 col-md-6 col-xl-3">
          <InsightCard {...card} />
        </div>
      ))}
    </div>
  );
}

export default InsightsPanel;
