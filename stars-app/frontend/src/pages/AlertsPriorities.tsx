import PageShell from "../components/layout/PageShell";
import AlertItemComponent from "../components/shared/AlertItem";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import ProgressBar from "../components/shared/ProgressBar";
import { useGetAlerts } from "../api/alerts";

export default function AlertsPriorities() {
  const { data, isLoading } = useGetAlerts();

  const critical = data?.alerts.filter(a => a.severity === "critical") ?? [];
  const warnings = data?.alerts.filter(a => a.severity === "warning") ?? [];
  const info = data?.alerts.filter(a => a.severity === "info") ?? [];

  return (
    <PageShell title="Alerts & Priorities" subtitle="Critical gaps, warning signals, and outreach opportunities">
      {isLoading ? <LoadingSpinner /> : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Alerts */}
          <div className="lg:col-span-2 space-y-5">
            {critical.length > 0 && (
              <div>
                <div className="section-title text-red-400">🔴 Critical ({critical.length})</div>
                <div className="space-y-2">{critical.map(a => <AlertItemComponent key={a.alert_id} item={a} />)}</div>
              </div>
            )}
            {warnings.length > 0 && (
              <div>
                <div className="section-title text-amber-400">🟡 Warnings ({warnings.length})</div>
                <div className="space-y-2">{warnings.map(a => <AlertItemComponent key={a.alert_id} item={a} />)}</div>
              </div>
            )}
            {info.length > 0 && (
              <div>
                <div className="section-title text-blue-400">🔵 Opportunities ({info.length})</div>
                <div className="space-y-2">{info.map(a => <AlertItemComponent key={a.alert_id} item={a} />)}</div>
              </div>
            )}
          </div>

          {/* Priority scoreboard */}
          <div className="space-y-4">
            <div className="card">
              <div className="section-title">Priority Scoreboard</div>
              <div className="space-y-3">
                {(data?.priority_board ?? []).map((p, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-white font-medium">{p.measure_code}</span>
                      <span className="text-muted text-xs">{p.current_rate.toFixed(1)}% / {p.target_rate.toFixed(1)}%</span>
                    </div>
                    <ProgressBar value={p.current_rate} target={p.target_rate} status={p.gap > 3 ? "red" : "yellow"} />
                    <div className="flex justify-between text-[10px] text-muted mt-0.5">
                      <span>{p.owner}</span>
                      <span>Score: {p.priority_score}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Time to act card */}
            <div className="card border-brand-amber">
              <div className="text-amber-400 font-semibold text-sm mb-1">⏱ Time to Act</div>
              <div className="text-3xl font-bold text-white">83 days</div>
              <div className="text-muted text-xs mt-1">Until Q2 2025 snapshot closes</div>
              <ProgressBar value={17} status="amber" />
              <div className="text-muted text-[10px] mt-1">17% of measurement window remaining</div>
            </div>
          </div>
        </div>
      )}
    </PageShell>
  );
}
