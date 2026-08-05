// RoadCard.jsx → SINGLE ROAD DISPLAY CARD

import tokens from "../styles/tokens";
import SignalLight from "./SignalLight";

function RoadCard({ road }) {
  const predictionStatusText =
    (road.predictionStatus || "").toLowerCase() === "success"
      ? "SUCCESS"
      : "Prediction Unavailable";

  const timerLabel = road.signal === "GREEN" ? "⏱ Remaining Time" : "⏳ Waiting Time";
  const timerValue = road.signal === "GREEN" ? road.remainingTime ?? 0 : road.waitingTime ?? 0;

  return (
    <div style={{
      background: tokens.card,
      border: `0.5px solid ${tokens.border}`,
      borderRadius: "16px",
      padding: "20px",
      textAlign: "center"
    }}>

      {/* ROAD NAME */}
      <h3>{road.name}</h3>

      {/* SIGNAL COMPONENT */}
      <SignalLight signal={road.signal} />

      {/* SIGNAL TEXT */}
      <h4 style={{
        color: road.signal === "GREEN"
          ? tokens.green
          : tokens.red
      }}>
        {road.signal}
      </h4>

      <p>🚗 Current Vehicles: {road.vehicleCount ?? 0}</p>
      <p>🔮 Predicted Vehicles: {road.predictedVehicleCount ?? 0}</p>
      <p>📉 Density: {road.densityLevel || "Unknown"}</p>
      <p>🧠 Prediction Status: {predictionStatusText}</p>
      <p>{timerLabel}: {timerValue} sec</p>

    </div>
  );
}

export default RoadCard;