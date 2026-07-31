import { Link } from "react-router-dom";

export default function Layout({ children }) {
  return (
    <div
      className="min-h-screen text-white"
      style={{
        background: "#020617",
        backgroundImage: `
          linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
        `,
        backgroundSize: "40px 40px",
      }}
    >
      {/* NAVBAR */}
      <div className="flex justify-between items-center px-10 py-5 border-b border-gray-800">
        <h2 className="font-semibold text-lg">🚦 AI Traffic</h2>

        <div className="flex gap-6 text-sm">
          <Link to="/">Home</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/analytics">Analytics</Link>
          <Link to="/upload">Upload</Link>
          <Link to="/members">Team</Link>
        </div>
      </div>

      {/* CENTER CONTENT */}
      <div className="max-w-6xl mx-auto px-6 py-16">
        {children}
      </div>
    </div>
  );
}