import PageShell from "../components/layout/PageShell";
import KPICard from "../components/shared/KPICard";
import StatusBadge from "../components/shared/StatusBadge";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import ProgressBar from "../components/shared/ProgressBar";
import { useGetCahpsOverview } from "../api/cahps";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from "recharts";
import { COLORS } from "../styles/tokens";

export default function CahpsOverview() {
  const { data, isLoading } = useGetCahpsOverview("H3312");

  if (isLoading) return <div className="p-8"><LoadingSpinner /></div>;
  if (!data) return null;

  const chartData = data.composites.map(c => ({
    name: c.composite_name.split(" ").slice(0, 3).join(" "),
    value: c.current_pct,
    fill: c.status === "ok" ? COLORS.teal : c.status === "risk" ? COLORS.amber : COLORS.red,
  }));

  return (
    <PageShell title="CAHPS Overview" subtitle="Member experience and satisfaction metrics · H3312 · PY2025">
      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KPICard label="Current Rating" value={`${data.current_rating.toFixed(1)} ★`} color="teal" />
        <KPICard label="Projected Rating" value={`${data.projected_rating.toFixed(1)} ★`} color="blue" />
        <KPICard label="Gap to 4-Star" value={data.gap_to_4_star > 0 ? `${data.gap_to_4_star.toFixed(1)} pts` : "On Track"} color={data.gap_to_4_star > 0 ? "amber" : "teal"} />
        <KPICard label="QBP at Stake" value={`$${(data.qbp_at_stake / 1_000_000).toFixed(2)}M`} color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Bar chart */}
        <div className="card lg:col-span-2">
          <div className="section-title">Composite Scores</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} margin={{ top: 4, right: 8, bottom: 32, left: 0 }} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3e52" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} width={100} />
              <ReferenceLine x={80} stroke="#ffffff30" strokeDasharray="4 4" label={{ value: "4★ target", fill: "#94a3b8", fontSize: 9 }} />
              <Tooltip
                contentStyle={{ background: "#1e2a3a", border: "1px solid #2d3e52", borderRadius: 8 }}
                formatter={(v: number) => [`${v.toFixed(1)}%`, "Score"]}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((d, i) => <Cell key={i} fill={d.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Days remaining */}
        <div className="space-y-4">
          <div className="card border-brand-amber text-center">
            <div className="text-amber-400 text-xs mb-1">Survey Window Closes In</div>
            <div className="text-5xl font-bold text-white">{data.days_remaining}</div>
            <div className="text-muted text-xs mt-1">days remaining</div>
            <div className="mt-3">
              <ProgressBar value={100 - data.days_remaining / 1.83} status="amber" />
            </div>
          </div>

          <div className="card">
            <div className="section-title text-sm">Composite Status</div>
            <div className="space-y-2">
              {data.composites.map(c => (
                <div key={c.composite_code} className="flex items-center justify-between gap-2">
                  <div className="text-xs text-slate-300 truncate flex-1">{c.composite_name}</div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-white text-xs font-medium">{c.current_pct.toFixed(1)}%</span>
                    <StatusBadge status={c.status} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Composite detail table */}
      <div className="card p-0 overflow-hidden">
        <table className="data-table">
          <thead>
            <tr><th>Composite</th><th>Code</th><th>Weight</th><th>Score</th><th>Status</th><th>Progress to 80%</th></tr>
          </thead>
          <tbody>
            {data.composites.map(c => (
              <tr key={c.composite_code}>
                <td className="text-white">{c.composite_name}</td>
                <td className="font-mono text-muted">{c.composite_code}</td>
                <td><span className="pill blue">{c.weight}</span></td>
                <td className="font-semibold text-white">{c.current_pct.toFixed(1)}%</td>
                <td><StatusBadge status={c.status} /></td>
                <td className="w-28"><ProgressBar value={c.current_pct} target={80} status={c.status === "ok" ? "green" : c.status === "risk" ? "yellow" : "red"} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageShell>
  );
}
