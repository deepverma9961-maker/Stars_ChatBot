import { useParams, useNavigate } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import StarRatingBadge from "../components/shared/StarRatingBadge";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import ComplianceLineChart from "../components/charts/ComplianceLineChart";
import StarRadarChart from "../components/charts/StarRadarChart";
import { useGetPlanDetail } from "../api/plans";
import { useGetHedisMeasures } from "../api/hedis";
import ProgressBar from "../components/shared/ProgressBar";
import StatusBadge from "../components/shared/StatusBadge";

export default function PlanDetail() {
  const { contractId = "H3312" } = useParams();
  const navigate = useNavigate();
  const { data: plan, isLoading } = useGetPlanDetail(contractId);
  const { data: hedis } = useGetHedisMeasures(contractId);

  if (isLoading) return <div className="p-8"><LoadingSpinner /></div>;
  if (!plan) return null;

  return (
    <PageShell
      title={plan.plan_name}
      subtitle={`${plan.contract_id} · ${plan.state} · ${(plan.enrollment / 1000).toFixed(1)}K members`}
      actions={
        <button onClick={() => navigate("/executive")} className="text-muted text-sm hover:text-white">← Back</button>
      }
    >
      {/* Hero row */}
      <div className="flex items-center gap-4 mb-6">
        <StarRatingBadge rating={plan.projected_rating} size="lg" />
        {plan.bonus_eligible && <span className="pill green">Bonus Eligible</span>}
        {plan.star_gap_to_4 > 0 && (
          <span className="text-amber-400 text-sm">▲ {plan.star_gap_to_4.toFixed(1)} pts to 4★</span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Historical trend */}
        <div className="card lg:col-span-1">
          <div className="section-title">Rating History</div>
          <ComplianceLineChart data={plan.historical_ratings} />
        </div>

        {/* Domain radar */}
        <div className="card lg:col-span-1">
          <div className="section-title">Domain Performance</div>
          <StarRadarChart domains={plan.domain_scores} />
        </div>

        {/* Domain cards */}
        <div className="lg:col-span-1 grid grid-cols-2 gap-3">
          {plan.domain_scores.map(d => (
            <div key={d.domain} className="card text-center">
              <div className="text-muted text-xs">{d.domain}</div>
              <div className="text-xl font-bold text-white my-1">{d.rating.toFixed(1)} ★</div>
              <div className="text-xs text-muted">{d.on_track_count}/{d.total_count} on track</div>
              {d.critical_count > 0 && <div className="text-xs text-red-400 mt-0.5">{d.critical_count} critical</div>}
            </div>
          ))}
        </div>
      </div>

      {/* HEDIS table */}
      {hedis && (
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-brand-border flex items-center justify-between">
            <div className="section-title mb-0">HEDIS Measures</div>
            <button onClick={() => navigate("/hedis")} className="text-xs text-muted hover:text-white">View All →</button>
          </div>
          <table className="data-table">
            <thead>
              <tr><th>Measure</th><th>Wt</th><th>Rate</th><th>Gaps</th><th>Status</th><th>Progress</th></tr>
            </thead>
            <tbody>
              {hedis.map(m => (
                <tr key={m.measure_code}>
                  <td className="text-white">{m.measure_name}</td>
                  <td><span className="pill blue">{m.weight}</span></td>
                  <td className="font-medium">{m.current_rate.toFixed(1)}%</td>
                  <td className="text-muted">{m.open_gap_count.toLocaleString()}</td>
                  <td><StatusBadge status={m.status} /></td>
                  <td className="w-28"><ProgressBar value={m.current_rate} target={m.target_rate} status={m.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageShell>
  );
}
