import { useEffect, useState } from "react";
import { getHealth } from "../api/trafficApi";

function BackendStatus() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    let isMounted = true;

    async function checkBackendHealth() {
      try {
        const data = await getHealth();

        if (isMounted) {
          setStatus(data && data.status === "Backend is running" ? "online" : "offline");
        }
      } catch (error) {
        if (isMounted) {
          setStatus("offline");
        }
      }
    }

    checkBackendHealth();

    return () => {
      isMounted = false;
    };
  }, []);

  const label =
    status === "online"
      ? "🟢 Backend Online"
      : status === "offline"
        ? "🔴 Backend Offline"
        : "🟡 Checking Backend...";

  return (
    <div
      style={{
        textAlign: "center",
        marginBottom: "20px",
        fontWeight: "600",
        color: status === "online" ? "#22c55e" : status === "offline" ? "#ef4444" : "#fbbf24",
      }}
    >
      {label}
    </div>
  );
}

export default BackendStatus;
