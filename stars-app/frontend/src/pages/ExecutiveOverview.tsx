import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import KPICard from "../components/shared/KPICard";
import StarRatingBadge from "../components/shared/StarRatingBadge";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import { useGetStarSummary } from "../api/starSummary";
import { useGetPlans } from "../api/plans";

const CONTRACT_IDS = ["H3312","H5521","H2213","H6614","H7723","H8812","H9914","H1045","H2156","H3267"];
const PY_RATINGS = [3, 3.5, 4, 4.5, 5];

function ratingClass(val: number): string {
  if (val >= 4.5) return "s5";
  if (val >= 4.0) return "s4";
  if (val >= 3.5) return "s35";
  return "s3";
}

function RatingCell({ value }: { value: number }) {
  return (
    <span className={`star-badge ${ratingClass(value)} text-xs px-1.5 py-0.5`}>
      {value.toFixed(1)}
    </span>
  );
}

export default function ExecutiveOverview() {
  const navigate = useNavigate();

  const [contractId, setContractId] = useState("");
  const [planName, setPlanName] = useState("");
  const [pyRating, setPyRating] = useState("");
  const [projRating, setProjRating] = useState("");

  const [appliedFilters, setAppliedFilters] = useState<{
    contractId: string; planName: string; pyRating: string; projRating: string;
  }>({ contractId: "", planName: "", pyRating: "", projRating: "" });

  const { data: summary } = useGetStarSummary();

  const { data: allPlans, isLoading } = useGetPlans({
    search: appliedFilters.planName || appliedFilters.contractId || undefined,
    py_rating: appliedFilters.pyRating ? Number(appliedFilters.pyRating) : undefined,
    proj_rating: appliedFilters.projRating ? Number(appliedFilters.projRating) : undefined,
  });

  const plans = (allPlans ?? []).filter(p =>
    !appliedFilters.contractId || p.contract_id === appliedFilters.contractId
  );

  function handleApply() {
    setAppliedFilters({ contractId, planName, pyRating, projRating });
  }

  function handleReset() {
    setContractId("");
    setPlanName("");
    setPyRating("");
    setProjRating("");
    setAppliedFilters({ contractId: "", planName: "", pyRating: "", projRating: "" });
  }

  return (
    <PageShell title="Executive Overview" subtitle="Top 14 contracts by enrollment · MY2025 · Excludes S-contracts">
      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KPICard label="TOTAL HEALTH PLANS"   value={summary?.total_plans ?? 14}  color="red" />
        <KPICard label="TOTAL ENROLLMENT"      value={summary ? `${(summary.total_enrollment / 1000).toFixed(0)}K` : "980K"} color="blue" />
        <KPICard label="CONTRACTS ABOVE 4★"   value={summary?.above_4star_count ?? 9}   color="teal" />
        <KPICard label="% CONTRACTS ABOVE 4★" value={summary ? `${summary.above_4star_pct}%` : "64%"} color="amber" />
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="flex flex-wrap gap-3 items-end">
          {/* Contract ID */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted uppercase tracking-wider">Contract ID</label>
            <select
              value={contractId}
              onChange={e => setContractId(e.target.value)}
              className="px-3 py-2 rounded-lg bg-brand-dark border border-brand-border text-white text-sm focus:outline-none min-w-36"
            >
              <option value="">All Contract IDs</option>
              {CONTRACT_IDS.map(id => <option key={id} value={id}>{id}</option>)}
            </select>
          </div>

          {/* Plan Name */}
          <div className="flex flex-col gap-1 flex-1 min-w-48">
            <label className="text-xs text-muted uppercase tracking-wider">Plan Name</label>
            <input
              value={planName}
              onChange={e => setPlanName(e.target.value)}
              placeholder="Search plan name..."
              className="px-3 py-2 rounded-lg bg-brand-dark border border-brand-border text-white text-sm placeholder:text-muted focus:outline-none focus:border-white/30"
            />
          </div>

          {/* PY Rating */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted uppercase tracking-wider">PY Rating</label>
            <select
              value={pyRating}
              onChange={e => setPyRating(e.target.value)}
              className="px-3 py-2 rounded-lg bg-brand-dark border border-brand-border text-white text-sm focus:outline-none min-w-36"
            >
              <option value="">All PY Ratings</option>
              {PY_RATINGS.map(r => <option key={r} value={r}>{r}★</option>)}
            </select>
          </div>

          {/* Projected Rating */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted uppercase tracking-wider">Projected Rating</label>
            <select
              value={projRating}
              onChange={e => setProjRating(e.target.value)}
              className="px-3 py-2 rounded-lg bg-brand-dark border border-brand-border text-white text-sm focus:outline-none min-w-36"
            >
              <option value="">All Projected</option>
              {PY_RATINGS.map(r => <option key={r} value={r}>{r}★</option>)}
            </select>
          </div>

          {/* Actions */}
          <div className="flex items-end gap-2">
            <button
              onClick={handleApply}
              className="px-4 py-2 rounded-lg text-white text-sm font-semibold transition-opacity hover:opacity-90"
              style={{ background: "#F26722" }}
            >
              Apply
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 rounded-lg border border-brand-border text-white text-sm font-medium hover:bg-white/5 transition"
            >
              Reset
            </button>
            <span className="text-xs text-muted px-2 py-2 whitespace-nowrap">
              {plans.length} plans
            </span>
          </div>
        </div>
      </div>

      {/* Table */}
      {isLoading ? <LoadingSpinner /> : (
        <div className="card p-0 overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Plan Name</th>
                <th>Contract ID</th>
                <th>State</th>
                <th>Enrollment</th>
                <th>PY Rating</th>
                <th>Projected</th>
                <th>HEDIS</th>
                <th>CAHPS</th>
                <th>HOS</th>
                <th>Part D</th>
              </tr>
            </thead>
            <tbody>
              {plans.map(p => (
                <tr key={p.contract_id} className="cursor-pointer" onClick={() => navigate(`/plan/${p.contract_id}`)}>
                  <td className="text-white font-medium">{p.plan_name}</td>
                  <td className="font-mono text-brand-teal font-medium">{p.contract_id}</td>
                  <td>{p.state}</td>
                  <td>{p.enrollment.toLocaleString()}</td>
                  <td><StarRatingBadge rating={p.py_rating} size="sm" /></td>
                  <td><StarRatingBadge rating={p.projected_rating} size="sm" /></td>
                  <td><RatingCell value={p.hedis_rating} /></td>
                  <td><RatingCell value={p.cahps_rating} /></td>
                  <td><RatingCell value={p.hos_rating} /></td>
                  <td><RatingCell value={p.partd_rating} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageShell>
  );
}
