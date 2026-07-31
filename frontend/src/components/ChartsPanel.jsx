import { useMemo } from "react";
import { BarChart, Bar, CartesianGrid, Cell, PieChart, Pie, ResponsiveContainer, Tooltip, XAxis, YAxis, LineChart, Line } from "recharts";
import ChartCard from "./ChartCard";

function ChartsPanel({ roads, trendData, hasTraffic }) {
  const densityDistribution = useMemo(() => {
    const counts = { LOW: 0, MEDIUM: 0, HIGH: 0 };
    roads.forEach((road) => {
      const density = (road.densityLevel || "UNKNOWN").toUpperCase();
      if (counts[density] !== undefined) {
        counts[density] += 1;
      }
    });

    return [
      { name: "LOW", value: counts.LOW, color: "#38bdf8" },
      { name: "MEDIUM", value: counts.MEDIUM, color: "#facc15" },
      { name: "HIGH", value: counts.HIGH, color: "#f87171" },
    ];
  }, [roads]);

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
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={densityDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={90} animationDuration={600} animationBegin={0}>
                    {densityDistribution.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
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
    </div>
  );
}

export default ChartsPanel;
