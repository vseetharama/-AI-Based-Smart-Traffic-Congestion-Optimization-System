import { useMemo } from "react";
import { BarChart, Bar, CartesianGrid, Cell, PieChart, Pie, ResponsiveContainer, Tooltip, XAxis, YAxis, LineChart, Line } from "recharts";
import ChartCard from "./ChartCard";

function ChartsPanel({ roads, trendData, hasTraffic, densityData = null, waitingTrend = [] }) {
  const getDensityColor = (name) => {
    const normalizedName = String(name || "").toUpperCase();
    if (normalizedName === "LOW") return "#22C55E";
    if (normalizedName === "MEDIUM") return "#FACC15";
    if (normalizedName === "HIGH") return "#EF4444";
    return "#60A5FA";
  };

  const densityDistribution = useMemo(() => {
    if (densityData?.length) {
      return densityData.map((item) => ({
        name: item.name || item.label || "UNKNOWN",
        value: item.value || 0,
        color: getDensityColor(item.name || item.label),
      }));
    }

    const counts = { LOW: 0, MEDIUM: 0, HIGH: 0 };
    roads.forEach((road) => {
      const density = (road.densityLevel || "UNKNOWN").toUpperCase();
      if (counts[density] !== undefined) {
        counts[density] += 1;
      }
    });

    return [
      { name: "LOW", value: counts.LOW, color: getDensityColor("LOW") },
      { name: "MEDIUM", value: counts.MEDIUM, color: getDensityColor("MEDIUM") },
      { name: "HIGH", value: counts.HIGH, color: getDensityColor("HIGH") },
    ];
  }, [roads, densityData]);

  const totalDensityRoads = useMemo(() => {
    return densityDistribution.reduce((sum, item) => sum + (Number(item.value) || 0), 0);
  }, [densityDistribution]);

  const legendItems = useMemo(() => {
    return densityDistribution.filter((item) => Number(item.value) > 0);
  }, [densityDistribution]);

  const vehicleBars = useMemo(() => {
    return roads.map((road) => ({
      name: road.name,
      vehicles: road.vehicleCount || 0,
    }));
  }, [roads]);

  return (
    <div className="row g-4">
      <div className="col-12 col-xl-6">
        <ChartCard title="Vehicles Per Road" subtitle="Live vehicle counts by monitored road">
          {hasTraffic ? (
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={vehicleBars} animationDuration={500}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="name" stroke="#cbd5e1" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
                  <YAxis stroke="#cbd5e1" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="vehicles" radius={[6, 6, 0, 0]} animationBegin={0} animationDuration={600}>
                    {vehicleBars.map((entry, index) => (
                      <Cell key={`${entry.name}-${index}`} fill={index % 2 === 0 ? "#60a5fa" : "#a78bfa"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="text-center text-muted py-5">No traffic data available</div>
          )}
        </ChartCard>
      </div>

      <div className="col-12 col-xl-6">
        <ChartCard title="Traffic Density Distribution" subtitle="Current density mix across monitored roads">
          {hasTraffic ? (
            <div className="d-flex flex-column align-items-center" style={{ width: "100%", minHeight: 320 }}>
              <div style={{ width: "100%", height: 260 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={densityDistribution}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      animationDuration={600}
                      animationBegin={0}
                      paddingAngle={2}
                    >
                      {densityDistribution.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value, name) => [`${value} roads`, name]}
                      contentStyle={{ backgroundColor: "rgba(15, 23, 42, 0.95)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "10px" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="d-flex flex-wrap justify-content-center gap-3 mt-2" style={{ width: "100%" }}>
                {legendItems.length > 0 ? (
                  legendItems.map((item) => {
                    const percentage = totalDensityRoads > 0 ? Math.round((Number(item.value) / totalDensityRoads) * 100) : 0;
                    return (
                      <div key={item.name} className="d-flex align-items-center gap-2 text-slate-300 small">
                        <span style={{ color: item.color, fontSize: "0.9rem" }}>●</span>
                        <span className="fw-semibold text-white">{item.name}</span>
                        <span>({item.value})</span>
                        <span className="text-slate-400">{percentage}%</span>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-slate-400 small">No density data available</div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-muted py-5">No traffic data available</div>
          )}
        </ChartCard>
      </div>

      <div className="col-12">
        <ChartCard title="Live Traffic Trend" subtitle="Last 30 polling updates of total vehicles">
          {trendData.length > 0 ? (
            <div style={{ width: "100%", height: 280 }}>
              <ResponsiveContainer>
                <LineChart data={trendData} animationDuration={500}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="label" stroke="#cbd5e1" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
                  <YAxis stroke="#cbd5e1" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="totalVehicles" stroke="#4ade80" strokeWidth={2} dot={false} animationDuration={500} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="text-center text-muted py-5">No traffic data available</div>
          )}
        </ChartCard>
      </div>

      {waitingTrend.length > 0 ? (
        <div className="col-12">
          <ChartCard title="Waiting Time Trend" subtitle="Average waiting time across the selected period">
            <div style={{ width: "100%", height: 280 }}>
              <ResponsiveContainer>
                <LineChart data={waitingTrend} animationDuration={500}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="time" stroke="#cbd5e1" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
                  <YAxis stroke="#cbd5e1" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="waiting" stroke="#f59e0b" strokeWidth={2} dot={false} animationDuration={500} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>
      ) : null}
    </div>
  );
}

export default ChartsPanel;
