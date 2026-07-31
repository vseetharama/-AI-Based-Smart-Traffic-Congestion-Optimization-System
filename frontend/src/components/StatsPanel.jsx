import StatsCard from "./StatsCard";

function formatTimestamp(timestamp) {
  if (!timestamp) return "Not available";

  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "Not available";

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function StatsPanel({ roads, status, lastUpdated, activeRoadId, currentTimer }) {
  const totalVehicles = roads.reduce((sum, road) => sum + (road.vehicleCount || 0), 0);
  const averageVehicles = roads.length ? (totalVehicles / roads.length).toFixed(1) : "0.0";
  const highestTrafficRoad = roads.reduce(
    (current, road) => {
      if (!current) return road;
      return (road.vehicleCount || 0) > (current.vehicleCount || 0) ? road : current;
    },
    null,
  );
  const highestDensity = roads.reduce(
    (current, road) => {
      const densityRank = { LOW: 1, MEDIUM: 2, HIGH: 3, UNKNOWN: 0 };
      const currentRank = densityRank[current?.densityLevel?.toUpperCase()] || 0;
      const roadRank = densityRank[road.densityLevel?.toUpperCase()] || 0;
      return roadRank > currentRank ? road : current;
    },
    null,
  );
  const hasTraffic = roads.some((road) => (road.vehicleCount || 0) > 0);
  const activeRoad = roads.find((road) => road.id === activeRoadId) || roads.find((road) => road.signal === "GREEN") || roads[0] || null;

  const summaryCards = [
    {
      title: "System Status",
      value: status === "RUNNING" ? "RUNNING" : "OFFLINE",
      icon: "🟢",
      subtitle: status === "RUNNING" ? "Polling is active" : "No fresh dashboard response",
      tone: status === "RUNNING" ? "success" : "danger",
    },
    {
      title: "Active Road",
      value: activeRoad ? activeRoad.name : "No active road",
      icon: "🛣️",
      subtitle: activeRoad ? `Signal: ${activeRoad.signal}` : "Waiting for data",
      tone: "default",
    },
    {
      title: "Current Timer",
      value: activeRoad ? `${activeRoad.timer ?? 0} sec` : "0 sec",
      icon: "⏱️",
      subtitle: activeRoad ? "Latest green-time value" : "No active timer",
      tone: "warning",
    },
    {
      title: "Highest Density",
      value: highestDensity ? highestDensity.densityLevel : "NONE",
      icon: "📈",
      subtitle: highestDensity ? `${highestDensity.name}` : "No traffic detected",
      tone: highestDensity?.densityLevel === "HIGH" ? "danger" : "default",
    },
  ];

  const statsCards = [
    {
      title: "Total Vehicles Detected",
      value: hasTraffic ? totalVehicles : "No traffic detected",
      icon: "🚗",
      subtitle: hasTraffic ? "Sum of all road vehicle counts" : "All roads are currently idle",
      tone: hasTraffic ? "success" : "default",
    },
    {
      title: "Average Vehicles per Road",
      value: hasTraffic ? `${averageVehicles}` : "0.0",
      icon: "📊",
      subtitle: hasTraffic ? "Average across monitored roads" : "No vehicle activity",
      tone: "default",
    },
    {
      title: "Highest Traffic Road",
      value: highestTrafficRoad ? highestTrafficRoad.name : "None",
      icon: "🏁",
      subtitle: highestTrafficRoad ? `${highestTrafficRoad.vehicleCount || 0} vehicles` : "No traffic detected",
      tone: "warning",
    },
    {
      title: "Roads Being Monitored",
      value: roads.length || 0,
      icon: "🧭",
      subtitle: "Number of roads in the dashboard",
      tone: "default",
    },
    {
      title: "Last Dashboard Update",
      value: formatTimestamp(lastUpdated),
      icon: "🕒",
      subtitle: "Newest available road timestamp",
      tone: "default",
    },
  ];

  return (
    <div style={{ marginTop: "24px", marginBottom: "24px" }}>
      <div className="card" style={{ background: "rgba(15, 23, 42, 0.92)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "24px", padding: "6px" }}>
        <div className="card-body" style={{ padding: "24px" }}>
          <div className="d-flex flex-column flex-lg-row justify-content-between align-items-start align-items-lg-center gap-3 mb-4">
            <div>
              <h3 style={{ margin: 0, color: "#f8fafc" }}>📈 Real-Time Statistics</h3>
              <p style={{ margin: "6px 0 0", color: "#94a3b8" }}>
                Derived from the live dashboard response and refreshed on every polling cycle.
              </p>
            </div>
          </div>

          <div className="card mb-4" style={{ background: "linear-gradient(135deg, rgba(59,130,246,0.18), rgba(168,85,247,0.16))", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "20px" }}>
            <div className="card-body" style={{ padding: "20px" }}>
              <div className="row g-3 align-items-center">
                <div className="col-12 col-lg-3">
                  <div style={{ fontSize: "0.9rem", color: "#cbd5e1" }}>System Status</div>
                  <div style={{ fontSize: "1.25rem", fontWeight: 700, color: status === "RUNNING" ? "#4ade80" : "#f87171" }}>{status === "RUNNING" ? "RUNNING" : "OFFLINE"}</div>
                </div>
                <div className="col-12 col-lg-3">
                  <div style={{ fontSize: "0.9rem", color: "#cbd5e1" }}>Active Road</div>
                  <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "#f8fafc" }}>{activeRoad ? activeRoad.name : "No active road"}</div>
                </div>
                <div className="col-12 col-lg-3">
                  <div style={{ fontSize: "0.9rem", color: "#cbd5e1" }}>Current Timer</div>
                  <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "#f8fafc" }}>{activeRoad ? `${activeRoad.timer ?? currentTimer ?? 0} sec` : "0 sec"}</div>
                </div>
                <div className="col-12 col-lg-3">
                  <div style={{ fontSize: "0.9rem", color: "#cbd5e1" }}>Highest Density</div>
                  <div style={{ fontSize: "1.25rem", fontWeight: 700, color: highestDensity?.densityLevel === "HIGH" ? "#f87171" : "#f8fafc" }}>{highestDensity ? highestDensity.densityLevel : "NONE"}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="row g-3 mb-3">
            {summaryCards.map((card) => (
              <div key={card.title} className="col-12 col-lg-6">
                <StatsCard {...card} />
              </div>
            ))}
          </div>

          <div className="row g-3">
            {statsCards.map((card) => (
              <div key={card.title} className="col-12 col-md-6 col-xl-4">
                <StatsCard {...card} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatsPanel;
