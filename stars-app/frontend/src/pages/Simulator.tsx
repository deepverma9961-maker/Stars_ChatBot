import { useState } from "react";
import PageShell from "../components/layout/PageShell";
import FilterPanel from "../components/shared/FilterPanel";
import KPICard from "../components/shared/KPICard";
import WaterfallChart from "../components/charts/WaterfallChart";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import ChannelChip from "../components/shared/ChannelChip";
import { useRunSimulator } from "../api/simulator";
import type { SimulatorConfig, SimulatorResult } from "../types/simulator";

const MEASURE_OPTIONS = [
  { value: "", label: "All HEDIS" },
  { value: "COL", label: "COL – Colorectal" },
  { value: "CBP", label: "CBP – Blood Pressure" },
  { value: "KED", label: "KED – Kidney Eval" },
  { value: "AMM", label: "AMM – ED Follow-up" },
  { value: "OMW", label: "OMW – Osteoporosis" },
  { value: "SPC", label: "SPC – Statin Therapy" },
  { value: "BCS", label: "BCS – Breast Cancer" },
  { value: "HBD", label: "HBD – Blood Sugar" },
];

const DEFAULT_CONFIG: SimulatorConfig = {
  contract_id: "H3312",
  measure_code: null,
  gap_statuses: ["Open", "Partial", "Borderline"],
  propensity_tiers: ["high", "medium", "low"],
  channels: ["Call", "SMS", "Email"],
  incentive: "None",
  suppressions: { recently_contacted: true, opted_out: true, already_closed: true },
};

export default function Simulator() {
  const [config, setConfig] = useState<SimulatorConfig>(DEFAULT_CONFIG);
  const [result, setResult] = useState<SimulatorResult | null>(null);
  const { mutate, isPending } = useRunSimulator();

  const run = () => mutate(config, { onSuccess: setResult });

  const setField = <K extends keyof SimulatorConfig>(k: K, v: SimulatorConfig[K]) =>
    setConfig(prev => ({ ...prev, [k]: v }));

  const toggleSupp = (k: keyof SimulatorConfig["suppressions"]) =>
    setConfig(prev => ({ ...prev, suppressions: { ...prev.suppressions, [k]: !prev.suppressions[k] } }));

  return (
    <PageShell
      title="Campaign Simulator"
      subtitle="Model outreach pool, closure forecast, and waterfall projection"
      actions={
        <button
          onClick={run}
          disabled={isPending}
          className="px-4 py-2 rounded-lg bg-brand-red text-white text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          {isPending ? "Running..." : "▶ Run Simulation"}
        </button>
      }
    >
      <div className="flex gap-6">
        {/* Left sidebar filters */}
        <div className="w-56 flex-shrink-0 space-y-1">
          <div className="card">
            <div className="section-title text-sm">Measure</div>
            <select
              value={config.measure_code ?? ""}
              onChange={e => setField("measure_code", e.target.value || null)}
              className="w-full px-2 py-1.5 rounded bg-brand-dark border border-brand-border text-white text-xs focus:outline-none"
            >
              {MEASURE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>

          <div className="card">
            <FilterPanel
              label="Gap Status"
              options={[{ value: "Open", label: "Open" }, { value: "Partial", label: "Partial" }, { value: "Borderline", label: "Borderline" }]}
              selected={config.gap_statuses}
              onChange={v => setField("gap_statuses", v as any)}
            />
            <FilterPanel
              label="Propensity"
              options={[{ value: "high", label: "High >75%" }, { value: "medium", label: "Med 40-75%" }, { value: "low", label: "Low <40%" }]}
              selected={config.propensity_tiers}
              onChange={v => setField("propensity_tiers", v as any)}
            />
            <FilterPanel
              label="Channels"
              options={[{ value: "Call", label: "Call" }, { value: "SMS", label: "SMS" }, { value: "Email", label: "Email" }]}
              selected={config.channels}
              onChange={v => setField("channels", v as any)}
            />
            <div className="mb-2">
              <div className="text-xs text-muted mb-2">Incentive</div>
              <select
                value={config.incentive}
                onChange={e => setField("incentive", e.target.value as any)}
                className="w-full px-2 py-1.5 rounded bg-brand-dark border border-brand-border text-white text-xs focus:outline-none"
              >
                <option>None</option>
                <option>$25 card</option>
                <option>$50 card</option>
              </select>
            </div>
          </div>

          <div className="card">
            <div className="text-xs text-muted mb-2">Suppressions</div>
            {(Object.keys(config.suppressions) as Array<keyof SimulatorConfig["suppressions"]>).map(k => (
              <div key={k} className="supp-row">
                <span className="text-xs text-slate-300 capitalize">{k.replace(/_/g, " ")}</span>
                <button
                  onClick={() => toggleSupp(k)}
                  className={`toggle ${config.suppressions[k] ? "on" : "off"}`}
                >
                  <span className={`toggle-thumb ${config.suppressions[k] ? "on" : "off"}`} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Main panel */}
        <div className="flex-1 min-w-0">
          {isPending && <LoadingSpinner label="Running simulation..." />}

          {!result && !isPending && (
            <div className="card text-center py-16">
              <div className="text-4xl mb-3">⚙️</div>
              <div className="text-white font-medium mb-1">Configure & Run Simulation</div>
              <div className="text-muted text-sm">Set your filters on the left, then click Run Simulation</div>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* KPIs */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <KPICard label="Net Outreach Pool" value={result.net_pool.toLocaleString()} color="blue" />
                <KPICard label="Est. Closures" value={result.estimated_closures.toLocaleString()} color="teal" />
                <KPICard label="Projected Rate" value={`${result.projected_rate.toFixed(1)}%`} color="teal" />
                <KPICard label="Rate Lift" value={`+${result.lift.toFixed(1)}%`} color="amber" />
              </div>

              {/* Waterfall */}
              <div className="card">
                <div className="section-title">4-Week Outreach Waterfall — {result.measure_name}</div>
                <WaterfallChart data={result.waterfall} />
              </div>

              {/* Segment table */}
              <div className="card p-0 overflow-hidden">
                <div className="px-4 py-3 border-b border-brand-border section-title mb-0">Outreach Segments</div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Segment</th><th>Members</th><th>Channel</th><th>Incentive</th>
                      <th>Est. Closures</th><th>Closure Rate</th><th>Est. Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.segments.map((s, i) => (
                      <tr key={i}>
                        <td className="text-white">{s.label}</td>
                        <td>{s.members}</td>
                        <td><ChannelChip channel={s.channel} /></td>
                        <td className="text-muted text-xs">{s.incentive}</td>
                        <td className="text-brand-teal font-medium">{s.estimated_closures}</td>
                        <td>{s.closure_rate_pct}%</td>
                        <td className="text-muted">${s.estimated_cost.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageShell>
  );
}
