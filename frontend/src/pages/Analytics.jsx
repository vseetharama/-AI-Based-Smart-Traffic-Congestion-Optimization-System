import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import BackendStatus from "../components/BackendStatus";
import SummaryPanel from "../components/SummaryPanel";
import InsightsPanel from "../components/InsightsPanel";
import ChartsPanel from "../components/ChartsPanel";
import { getDashboard } from "../api/trafficApi";

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

function Analytics() {
  const navigate = useNavigate();
  const [roads, setRoads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dashboardData, setDashboardData] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const isMountedRef = useRef(false);
  const isFetchingRef = useRef(false);
  const hasInitialLoadRef = useRef(false);

  useEffect(() => {
    isMountedRef.current = true;

    const fetchDashboardData = async (isInitialFetch = false) => {
      if (isFetchingRef.current) {
        return;
      }

      isFetchingRef.current = true;

      try {
        if (isInitialFetch && !hasInitialLoadRef.current) {
          setLoading(true);
        }
        setError("");

        const data = await getDashboard();

        if (!isMountedRef.current) {
          return;
        }

        setDashboardData(data || null);

        const summaries = data?.road_summaries || {};
        const mappedRoads = Object.entries(summaries)
          .sort(([left], [right]) => left.localeCompare(right))
          .map(([roadId, summary]) => ({
            id: roadId,
            name: `Road ${roadId.replace("road", "")}`,
            signal: (summary?.signal_status || "RED").toUpperCase(),
            vehicleCount: summary?.vehicle_count ?? 0,
            densityLevel: summary?.density_level || "UNKNOWN",
            lastUpdated: summary?.last_updated || null,
          }));

        const totalVehicles = mappedRoads.reduce((sum, road) => sum + (road.vehicleCount || 0), 0);

        setTrendData((previous) => {
          const next = [...previous, { label: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }), totalVehicles }];
          return next.slice(-30);
        });

        hasInitialLoadRef.current = true;
        setLoading(false);
        setRoads(mappedRoads);
      } catch (err) {
        if (!isMountedRef.current) {
          return;
        }

        setError("Unable to load analytics data.");
        setDashboardData(null);
        setRoads([]);
      } finally {
        if (isMountedRef.current && !hasInitialLoadRef.current) {
          setLoading(false);
        }
        isFetchingRef.current = false;
      }
    };

    fetchDashboardData(true);

    const intervalId = window.setInterval(() => {
      fetchDashboardData(false);
    }, 1000);

    return () => {
      isMountedRef.current = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const metrics = useMemo(() => {
    const totalVehicles = roads.reduce((sum, road) => sum + (road.vehicleCount || 0), 0);
    const averageVehicles = roads.length ? (totalVehicles / roads.length).toFixed(1) : "0.0";
    const activeRoad = roads.find((road) => road.id === dashboardData?.current_green_road) || roads.find((road) => road.signal === "GREEN") || roads[0] || null;
    const highestTrafficRoad = roads.reduce((current, road) => {
      if (!current) return road;
      return (road.vehicleCount || 0) > (current.vehicleCount || 0) ? road : current;
    }, null);
    const leastBusyRoad = roads.reduce((current, road) => {
      if (!current) return road;
      return (road.vehicleCount || 0) < (current.vehicleCount || 0) ? road : current;
    }, null);
    const highestDensityRoad = roads.reduce((current, road) => {
      const densityRank = { LOW: 1, MEDIUM: 2, HIGH: 3, UNKNOWN: 0 };
      const currentRank = densityRank[current?.densityLevel?.toUpperCase()] || 0;
      const roadRank = densityRank[road.densityLevel?.toUpperCase()] || 0;
      return roadRank > currentRank ? road : current;
    }, null);
    const latestTimestamp = roads.reduce((latest, road) => {
      if (!road.lastUpdated) return latest;
      if (!latest) return road.lastUpdated;
      return new Date(road.lastUpdated) > new Date(latest) ? road.lastUpdated : latest;
    }, null);

    return {
      totalVehicles: totalVehicles || 0,
      averageVehicles,
      activeRoad: activeRoad ? activeRoad.name : "None",
      highestTrafficRoad: highestTrafficRoad ? highestTrafficRoad.name : "None",
      leastBusyRoad: leastBusyRoad ? leastBusyRoad.name : "None",
      highestDensity: highestDensityRoad ? highestDensityRoad.densityLevel : "NONE",
      currentTimer: dashboardData?.current_timer ?? 0,
      roadCount: roads.length,
      systemStatus: error ? "OFFLINE" : "RUNNING",
      lastUpdated: latestTimestamp ? formatTimestamp(latestTimestamp) : "Not available",
      hasTraffic: roads.some((road) => (road.vehicleCount || 0) > 0),
    };
  }, [roads, dashboardData, error]);

  return (
    <Layout>
      <div className="text-center mb-5">
        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-white mb-2">
          Real-Time Traffic Analytics
        </h1>
        <p className="text-slate-400 text-base md:text-lg max-w-2xl mx-auto">
          Live insights derived from the existing dashboard polling response.
        </p>
      </div>

      <BackendStatus />

      <div className="d-flex justify-content-center mb-4">
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="btn btn-outline-light btn-sm px-3 py-2"
        >
          ← Back to Live Dashboard
        </button>
      </div>

      {loading && <div className="text-center text-slate-300 mb-4">Loading analytics data...</div>}
      {error && <div className="text-center text-danger mb-4">{error}</div>}

      <SummaryPanel metrics={metrics} status={metrics.systemStatus} lastUpdated={metrics.lastUpdated} />
      <InsightsPanel metrics={metrics} />

      {metrics.hasTraffic ? (
        <ChartsPanel roads={roads} trendData={trendData} hasTraffic={metrics.hasTraffic} />
      ) : (
        <div className="card mb-4" style={{ background: "rgba(10, 14, 24, 0.94)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "20px", boxShadow: "0 10px 30px rgba(2, 8, 23, 0.35)" }}>
          <div className="card-body p-4 text-center text-slate-300">
            No traffic data available
          </div>
        </div>
      )}

      <div className="card mt-3" style={{ background: "rgba(10, 14, 24, 0.94)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "20px", boxShadow: "0 10px 30px rgba(2, 8, 23, 0.35)" }}>
        <div className="card-body p-4">
          <h4 className="mb-3 text-white fw-semibold">Future Analytics Modules</h4>
          <div className="row g-3">
            {[
              "Historical Analytics",
              "Daily Traffic",
              "Weekly Traffic",
              "Monthly Reports",
              "Peak Traffic Hour",
              "Average Waiting Time",
              "Signal Change History",
              "Traffic Reports",
            ].map((item) => (
              <div key={item} className="col-12 col-md-6 col-xl-4">
                <div className="p-3 rounded-3 border border-white/10 bg-white/5 text-slate-300">
                  {item}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Analytics;
