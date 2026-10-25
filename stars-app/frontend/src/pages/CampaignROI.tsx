import { useState } from "react";
import PageShell from "../components/layout/PageShell";
import KPICard from "../components/shared/KPICard";
import StatusBadge from "../components/shared/StatusBadge";
import ChannelChip from "../components/shared/ChannelChip";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import { useGetCampaigns } from "../api/campaigns";

export default function CampaignROI() {
  const [statusFilter, setStatusFilter] = useState("all");
  const { data, isLoading } = useGetCampaigns(statusFilter);

  return (
    <PageShell title="Campaign ROI" subtitle="Outreach campaign performance and return on investment">
      {/* Summary KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KPICard label="Total Members" value={data?.summary.total_members.toLocaleString() ?? "—"} color="blue" />
        <KPICard label="Total Closures" value={data?.summary.total_closures.toLocaleString() ?? "—"} color="teal" />
        <KPICard label="Avg ROI" value={data?.summary.avg_roi ?? "—"} color="amber" />
        <KPICard label="Total Cost" value={data?.summary.total_cost ?? "—"} color="red" />
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {["all", "Active", "Completed"].map(s => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`fchip ${statusFilter === s ? "on" : ""}`}
          >
            {s === "all" ? "All Campaigns" : s}
          </button>
        ))}
      </div>

      {isLoading ? <LoadingSpinner /> : (
        <div className="card p-0 overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Measure</th>
                <th>Channel</th>
                <th>Members</th>
                <th>Projected</th>
                <th>Actual</th>
                <th>Lift</th>
                <th>Cost</th>
                <th>ROI</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(data?.items ?? []).map((c, i) => (
                <tr key={i}>
                  <td className="text-white font-medium">{c.campaign_name}</td>
                  <td><span className="pill blue">{c.measure_code}</span></td>
                  <td><ChannelChip channel={c.channel} /></td>
                  <td>{c.member_count.toLocaleString()}</td>
                  <td className="text-muted">{c.projected_closures}</td>
                  <td className="text-brand-teal font-medium">{c.actual_closures ?? "—"}</td>
                  <td className="text-brand-teal">{c.lift_pct}</td>
                  <td className="text-muted">{c.cost_str}</td>
                  <td className="font-bold text-white">{c.roi_str}</td>
                  <td><StatusBadge status={c.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageShell>
  );
}
