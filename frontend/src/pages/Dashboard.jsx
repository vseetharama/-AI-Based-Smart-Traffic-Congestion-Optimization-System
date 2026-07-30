import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import RoadCard from "../components/RoadCard";
import BackendStatus from "../components/BackendStatus";

function Dashboard() {
  const [roads, setRoads] = useState([
    { name: "Road 1", signal: "GREEN", timer: 10, prediction: "Peak soon" },
    { name: "Road 2", signal: "RED", timer: 10, prediction: "Normal" },
    { name: "Road 3", signal: "RED", timer: 10, prediction: "Low traffic" },
    { name: "Road 4", signal: "RED", timer: 10, prediction: "Normal" }
  ]);

  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setRoads(prev => {
        let updated = [...prev];

        updated[activeIndex].timer--;

        if (updated[activeIndex].timer <= 0) {
          updated[activeIndex].signal = "RED";
          updated[activeIndex].timer = 10;

          let next = (activeIndex + 1) % 4;
          updated[next].signal = "GREEN";

          setActiveIndex(next);
        }

        return updated;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [activeIndex]);

  return (
    <Layout>

      <h1 style={{ textAlign: "center", marginBottom: "20px" }}>
        🚦 AI Traffic Control System (Live Demo)
      </h1>

      <BackendStatus />

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