import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import ProgressBar from "../components/shared/ProgressBar";
import StatusBadge from "../components/shared/StatusBadge";
import { useGetHedisMeasures } from "../api/hedis";

const COLOR_FILTERS = [
  { value: "all", label: "All Measures" },
  { value: "green", label: "On Track" },
  { value: "yellow", label: "At Risk" },
  { value: "red", label: "Critical" },
];

export default function HedisMeasures() {
  const [colorFilter, setColorFilter] = useState("all");
  const [sort, setSort] = useState<"rate_asc" | "rate_desc">("rate_asc");
  const navigate = useNavigate();
  const { data: measures, isLoading } = useGetHedisMeasures("H3312", colorFilter, sort);

  const counts = {
    green: measures?.filter(m => m.status === "green").length ?? 0,
    yellow: measures?.filter(m => m.status === "yellow").length ?? 0,
    red: measures?.filter(m => m.status === "red").length ?? 0,
  };
  const totalGaps = measures?.reduce((s, m) => s + m.open_gap_count, 0) ?? 0;

  return (
    <PageShell title="HEDIS Measures" subtitle="Clinical quality measure performance · H3312 · PY2025">
      {/* Summary stats */}
      <div className="grid grid-cols-4 gap-3 mb-5">
        <div className="card text-center">
          <div className="text-muted text-xs">Total Measures</div>
          <div className="text-2xl font-bold text-white">{measures?.length ?? 14}</div>
        </div>
        <div className="card text-center">
          <div className="text-muted text-xs">On Track</div>
          <div className="text-2xl font-bold text-brand-teal">{counts.green}</div>
        </div>
        <div className="card text-center">
          <div className="text-muted text-xs">At Risk</div>
          <div className="text-2xl font-bold text-brand-amber">{counts.yellow}</div>
        </div>
        <div className="card text-center">
          <div className="text-muted text-xs">Critical</div>
          <div className="text-2xl font-bold text-red-400">{counts.red}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-2">
          {COLOR_FILTERS.map(f => (
            <button
              key={f.value}
              onClick={() => setColorFilter(f.value)}
              className={`fchip ${colorFilter === f.value ? "on" : ""}`}
            >
              {f.label}
            </button>
          ))}
        </div>
        <button
          onClick={() => setSort(s => s === "rate_asc" ? "rate_desc" : "rate_asc")}
          className="text-xs text-muted hover:text-white border border-brand-border px-3 py-1 rounded-full"
        >
          Rate {sort === "rate_asc" ? "↑" : "↓"}
        </button>
      </div>

      {/* Total open gaps */}
      <div className="mb-4 text-xs text-muted">
        {totalGaps.toLocaleString()} total open gaps across filtered measures
      </div>

      {isLoading ? <LoadingSpinner /> : (
        <div className="card p-0 overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Measure</th>
                <th>Part</th>
                <th>Wt</th>
                <th>Rate</th>
                <th>Target</th>
                <th>Projected</th>
                <th>Open Gaps</th>
                <th>Status</th>
                <th>Progress</th>
              </tr>
            </thead>
            <tbody>
              {(measures ?? []).map(m => (
                <tr
                  key={m.measure_code}
                  className="cursor-pointer"
                  onClick={() => navigate(`/simulator?measure=${m.measure_code}`)}
                >
                  <td>
                    <div className="text-white font-medium text-sm">{m.measure_name}</div>
                    <div className="text-muted text-[10px]">{m.measure_code}</div>
                  </td>
                  <td className="text-muted">Part {m.part}</td>
                  <td><span className={`pill ${m.weight === "3x" ? "red" : "blue"}`}>{m.weight}</span></td>
                  <td className="font-semibold text-white">{m.current_rate.toFixed(1)}%</td>
                  <td className="text-muted">{m.target_rate.toFixed(1)}%</td>
                  <td className="text-brand-teal">{m.projected_rate.toFixed(1)}%</td>
                  <td className="text-muted">{m.open_gap_count.toLocaleString()}</td>
                  <td><StatusBadge status={m.status} /></td>
                  <td className="w-28">
                    <ProgressBar value={m.current_rate} target={m.target_rate} status={m.status} showLabel={false} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageShell>
  );
}
