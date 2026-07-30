import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import RoadCard from "../components/RoadCard";
import BackendStatus from "../components/BackendStatus";
import { getDashboard } from "../api/trafficApi";

function Dashboard() {
  const [roads, setRoads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function fetchDashboardData() {
      try {
        setLoading(true);
        setError("");

        const data = await getDashboard();

        if (!isMounted) {
          return;
        }

        const summaries = data?.road_summaries || {};
        const mappedRoads = Object.entries(summaries)
          .sort(([left], [right]) => left.localeCompare(right))
          .map(([roadId, summary]) => ({
            id: roadId,
            name: `Road ${roadId.replace("road", "")}`,
            signal: (summary?.signal_status || "RED").toUpperCase(),
            timer:
              data?.current_green_road === roadId
                ? data?.current_timer ?? summary?.recommended_green_time ?? 0
                : summary?.recommended_green_time ?? 0,
            vehicleCount: summary?.vehicle_count ?? 0,
            densityLevel: summary?.density_level || "UNKNOWN",
            densityScore: summary?.density_score ?? 0,
            prediction: summary?.prediction || "unknown",
            recommendedGreenTime: summary?.recommended_green_time ?? 0,
            lastUpdated: summary?.last_updated || null,
          }));

        setRoads(mappedRoads);
      } catch (err) {
        if (!isMounted) {
          return;
        }

        setError("Unable to load dashboard data.");
        setRoads([]);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchDashboardData();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <Layout>

      <h1 style={{ textAlign: "center", marginBottom: "20px" }}>
        🚦 AI Traffic Control System (Live Demo)
      </h1>

      <BackendStatus />

      {loading && (
        <div style={{ textAlign: "center", marginBottom: "20px", color: "#cbd5e1" }}>
          Loading dashboard data...
        </div>
      )}

      {error && (
        <div style={{ textAlign: "center", marginBottom: "20px", color: "#f87171" }}>
          {error}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px"
        }}
      >
        {roads.map((road, i) => (
          <RoadCard key={i} road={road} />
        ))}
      </div>

    </Layout>
  );
}

export default Dashboard;