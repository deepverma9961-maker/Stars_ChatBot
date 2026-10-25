import { NavLink } from "react-router-dom";

const NAV = [
  { path: "/marketing",  label: "Marketing Overview" },
  { path: "/executive",  label: "Executive" },
  { path: "/plan/H3312", label: "Plan Detail" },
  { path: "/hedis",      label: "HEDIS Measures" },
  { path: "/simulator",  label: "Simulator" },
  { path: "/agent",      label: "Agent Execution" },
  { path: "/projector",  label: "Impact Projector" },
  { path: "/campaigns",  label: "Campaign History & ROI" },
  { path: "/alerts",     label: "Alerts & Priorities" },
  { path: "/members",    label: "Member Gap List" },
  { path: "/cahps",      label: "CAHPS Overview" },
];

export default function Sidebar() {
  return (
    <aside className="w-56 flex-shrink-0 flex flex-col h-screen bg-brand-navy border-r border-brand-border">
      {/* Brand */}
      <div className="px-4 py-5 border-b border-brand-border">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-brand-red flex items-center justify-center text-white text-sm font-bold">S</div>
          <div>
            <div className="text-white font-bold text-sm leading-none">StarPulse</div>
            <div className="text-slate-400 text-[10px]">Medicare Stars Platform</div>
          </div>
        </div>
      </div>

      {/* Live status */}
      <div className="px-4 py-2 border-b border-brand-border flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-brand-red animate-pulse" />
        <span className="text-[11px] text-slate-400">Live · PY2025</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {NAV.map(({ path, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => `ntab ${isActive ? "active" : ""}`}
          >
            <span className="truncate">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-brand-border text-[10px] text-slate-500">
        Snapshot: Oct 15 · 83 days left
      </div>
    </aside>
  );
}
