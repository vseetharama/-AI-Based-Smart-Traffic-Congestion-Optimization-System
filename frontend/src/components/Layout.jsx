import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";

const links = [
  { to: "/", label: "Home" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/analytics", label: "Analytics" },
  { to: "/upload", label: "Upload" },
  { to: "/members", label: "Team" },
];

export default function Layout({ children }) {
  const location = useLocation();

  return (
    <div
      className="min-h-screen w-full max-w-full overflow-x-hidden text-white"
      style={{
        background: "#020617",
        backgroundImage: `
          linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
        `,
        backgroundSize: "40px 40px",
      }}
    >
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 px-4 py-4 sm:px-6 lg:px-10">
        <div className="flex min-w-0 items-center gap-2">
          <span className="text-lg leading-none sm:text-xl">🚦</span>
          <h2 className="whitespace-nowrap text-sm font-semibold leading-none tracking-tight text-white sm:text-base lg:text-[1.02rem]">
            <span className="hidden lg:inline">AI-Based Smart Traffic Congestion Optimization System</span>
            <span className="hidden md:inline lg:hidden">AI-Based Smart Traffic System</span>
            <span className="inline md:hidden">AI Traffic</span>
          </h2>
        </div>

        <div className="ml-auto flex flex-wrap items-center justify-end gap-3 text-sm sm:gap-4 lg:gap-6">
          {links.map((link) => {
            const isActive = location.pathname === link.to;
            return (
              <Link key={link.to} to={link.to} className="nav-link group relative text-slate-200 transition-colors hover:text-white">
                <span>{link.label}</span>
                <motion.span
                  className="absolute bottom-[-0.25rem] left-0 h-[2px] rounded-full bg-cyan-400"
                  initial={false}
                  animate={{ width: isActive ? "100%" : "0%" }}
                  transition={{ duration: 0.25 }}
                />
              </Link>
            );
          })}
        </div>
      </div>

      <div className="w-full max-w-full px-4 py-16 sm:px-6 lg:px-8 xl:px-10">
        {children}
      </div>
    </div>
  );
}