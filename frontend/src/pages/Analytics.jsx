import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import BackendStatus from "../components/BackendStatus";
import SummaryPanel from "../components/SummaryPanel";
import InsightsPanel from "../components/InsightsPanel";
import ChartsPanel from "../components/ChartsPanel";
import InsightCard from "../components/InsightCard";
import { getDashboard, getAnalyticsToday, getAnalyticsWeekly, getAnalyticsMonthly, exportAnalyticsReport } from "../api/trafficApi";

import { formatTimestamp, formatTime } from "../utils/dateUtils";

function Analytics() {
  const navigate = useNavigate();
  const [roads, setRoads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dashboardData, setDashboardData] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [selectedView, setSelectedView] = useState("today");
  const [historicalSummary, setHistoricalSummary] = useState(null);
  const [historicalCharts, setHistoricalCharts] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");
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

        if (selectedView !== "live") {
          let response;
          if (selectedView === "today") {
            response = await getAnalyticsToday();
          } else if (selectedView === "weekly") {
            response = await getAnalyticsWeekly();
          } else {
            response = await getAnalyticsMonthly();
          }

          if (!isMountedRef.current) {
            return;
          }

          const payload = response?.summary ? response : null;
          setHistoricalSummary(payload?.summary || null);
          setHistoricalCharts(payload?.charts || null);
          setDashboardData(null);
          setRoads([]);
          setTrendData([]);
          setLoading(false);
          return;
        }

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
          const next = [...previous, { label: formatTime(new Date()), totalVehicles }];
          return next.slice(-30);
        });

        hasInitialLoadRef.current = true;
        setLoading(false);
        setRoads(mappedRoads);
      } catch (err) {
        if (!isMountedRef.current) {
          return;
        }

        setError(err.message || "Unable to load analytics data.");
        setDashboardData(null);
        setRoads([]);
        setHistoricalSummary(null);
        setHistoricalCharts(null);
      } finally {
        if (isMountedRef.current && !hasInitialLoadRef.current) {
          setLoading(false);
        }
        isFetchingRef.current = false;
      }
    };

    if (selectedView === "live") {
      fetchDashboardData(true);

      const intervalId = window.setInterval(() => {
        fetchDashboardData(false);
      }, 1000);

      return () => {
        isMountedRef.current = false;
        window.clearInterval(intervalId);
      };
    }

    fetchDashboardData(true);

    return () => {
      isMountedRef.current = false;
    };
  }, [selectedView]);

  const handleExport = async (format) => {
    if (selectedView === "live") {
      setExportError("Export is available for historical views only.");
      return;
    }

    try {
      setExporting(true);
      setExportError("");
      const response = await exportAnalyticsReport(format, selectedView);

      const mimeType = response.contentType || (format === "pdf" ? "application/pdf" : "text/csv;charset=utf-8");
      const blob = response.blob instanceof Blob ? response.blob : new Blob([response.blob], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = response.filename || `traffic-report-${selectedView}.${format}`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err.message || "Unable to export report.");
    } finally {
      setExporting(false);
    }
  };

  const metrics = useMemo(() => {
    if (selectedView !== "live") {
      const summary = historicalSummary || {};
      return {
        totalVehicles: summary.totalVehicles || 0,
        averageVehicles: summary.averageVehicles?.toString() || "0.0",
        activeRoad: summary.highestTrafficRoad || "None",
        highestTrafficRoad: summary.highestTrafficRoad || "None",
        leastBusyRoad: summary.leastBusyRoad || "None",
        highestDensity: summary.highestDensity || "NONE",
        currentTimer: 0,
        roadCount: summary.roadCount || 0,
        systemStatus: error ? "OFFLINE" : "RUNNING",
        lastUpdated: summary.lastUpdated ? formatTimestamp(summary.lastUpdated) : "Not available",
        hasTraffic: (summary.totalVehicles || 0) > 0,
      };
    }

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
  }, [roads, dashboardData, error, selectedView, historicalSummary]);

  const overviewCards = [
    {
      title: "System Status",
      value: metrics.systemStatus || "RUNNING",
      icon: "🟢",
      subtitle: metrics.systemStatus === "RUNNING" ? "Live dashboard polling active" : "No fresh data received",
      tone: "success",
    },
    {
      title: "Current Active Road",
      value: metrics.activeRoad || "None",
      icon: "🛣️",
      subtitle: metrics.activeRoad ? "Current green road from the dashboard" : "Waiting for live data",
      tone: "primary",
    },
    {
      title: "Current Signal Timer",
      value: metrics.currentTimer ? `${metrics.currentTimer} sec` : "0 sec",
      icon: "⏱️",
      subtitle: "Live timer from the current signal cycle",
      tone: "warning",
    },
    {
      title: "Total Vehicles",
      value: metrics.totalVehicles || "No traffic data available",
      icon: "🚗",
      subtitle: metrics.totalVehicles ? "Combined live vehicle count" : "All roads are idle",
      tone: "success",
    },
    {
      title: "Highest Density",
      value: metrics.highestDensity || "NONE",
      icon: "📈",
      subtitle: metrics.highestDensity ? "Highest density detected among roads" : "No traffic detected",
      tone: metrics.highestDensity === "HIGH" ? "danger" : "default",
    },
    {
      title: "Last Updated",
      value: metrics.lastUpdated || "Not available",
      icon: "🕒",
      subtitle: "Most recent dashboard timestamp",
      tone: "secondary",
    },
  ];

  const secondaryCards = [
    {
      title: "Average Vehicles",
      value: metrics.averageVehicles || "0.0",
      icon: "📊",
      subtitle: "Average per monitored road",
      tone: "primary",
    },
    {
      title: "Highest Traffic Road",
      value: metrics.highestTrafficRoad || "None",
      icon: "🏁",
      subtitle: "Road with the most vehicles",
      tone: "warning",
    },
    {
      title: "Least Busy Road",
      value: metrics.leastBusyRoad || "None",
      icon: "🌿",
      subtitle: "Road with the fewest vehicles",
      tone: "success",
    },
    {
      title: "Roads Being Monitored",
      value: metrics.roadCount || 0,
      icon: "🧭",
      subtitle: "Number of monitored roads",
      tone: "secondary",
    },
  ];

  const hasWaitingTrendData = (historicalCharts?.waitingTrend || []).length > 0;

  return (
    <Layout>
      <div className="text-center mb-4">
        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-white mb-2">
          Real-Time Traffic Analytics
        </h1>
        <p className="text-slate-400 text-base md:text-lg max-w-3xl mx-auto">
          Real-time and historical traffic insights powered by YOLO vehicle detection and MongoDB analytics.
        </p>
      </div>

      <BackendStatus />

      <div className="d-flex justify-content-center mb-4">
        <div className="btn-group" role="group" aria-label="Analytics navigation">
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="btn btn-outline-light btn-sm px-3 py-2"
          >
            ← Back to Live Dashboard
          </button>
          <div className="btn-group" role="group" aria-label="Analytics view selector">
            {[
              { value: "live", label: "Live" },
              { value: "today", label: "Today" },
              { value: "weekly", label: "Weekly" },
              { value: "monthly", label: "Monthly" },
            ].map((option) => (
              <button
                key={option.value}
                type="button"
                className={`btn btn-sm ${selectedView === option.value ? "btn-light text-dark" : "btn-outline-light"}`}
                onClick={() => setSelectedView(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
          <div className="btn-group" role="group" aria-label="Analytics export actions">
            <button
              type="button"
              className="btn btn-outline-light btn-sm px-3 py-2"
              onClick={() => handleExport("pdf")}
              disabled={exporting || selectedView === "live"}
            >
              {exporting ? "Generating PDF..." : "Export PDF"}
            </button>
            <button
              type="button"
              className="btn btn-outline-light btn-sm px-3 py-2"
              onClick={() => handleExport("csv")}
              disabled={exporting || selectedView === "live"}
            >
              {exporting ? "Generating CSV..." : "Export CSV"}
            </button>
          </div>
        </div>
      </div>

      {exportError && (
        <div className="text-center text-danger mb-4">{exportError}</div>
      )}

      {loading && (
        <div className="text-center text-slate-300 mb-4">
          <div className="spinner-border spinner-border-sm text-light me-2" role="status" aria-hidden="true" />
          Loading analytics data...
        </div>
      )}
      {error && (
        <div className="text-center text-danger mb-4">
          {error}
          <button type="button" className="btn btn-outline-light btn-sm ms-3" onClick={() => setSelectedView(selectedView)}>
            Retry
          </button>
        </div>
      )}

      <div className="row g-3 mb-4">
        {overviewCards.map((card) => (
          <div key={card.title} className="col-12 col-md-6 col-xl-4">
            <InsightCard {...card} />
          </div>
        ))}
      </div>

      <div className="row g-3 mb-4">
        {secondaryCards.map((card) => (
          <div key={card.title} className="col-12 col-md-6 col-xl-3">
            <InsightCard {...card} />
          </div>
        ))}
      </div>

      <div className="row g-4">
        <div className="col-12">
          <ChartsPanel
            roads={selectedView === "live" ? roads : (historicalCharts?.roadDistribution?.map((item) => ({
              id: item.road,
              name: item.road,
              vehicleCount: item.vehicles,
              densityLevel: "UNKNOWN",
            })) || [])}
            trendData={selectedView === "live" ? trendData : (historicalCharts?.trafficTrend?.map((item) => ({ label: item.time, totalVehicles: item.vehicles })) || [])}
            densityData={selectedView === "live" ? null : (historicalCharts?.densityDistribution || [])}
            waitingTrend={selectedView === "live" ? [] : (historicalCharts?.waitingTrend || [])}
            hasTraffic={selectedView === "live" ? metrics.hasTraffic : (historicalSummary?.totalVehicles || 0) > 0}
          />
        </div>
      </div>

      {selectedView !== "live" && !hasWaitingTrendData && (
        <div className="mt-3 text-center text-slate-400 small">
          Waiting time analytics will appear once sufficient historical data is available.
        </div>
      )}
    </Layout>
  );
}

export default Analytics;
