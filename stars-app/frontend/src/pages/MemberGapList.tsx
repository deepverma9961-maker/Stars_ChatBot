import { useState } from "react";
import PageShell from "../components/layout/PageShell";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import StatusBadge from "../components/shared/StatusBadge";
import ChannelChip from "../components/shared/ChannelChip";
import MemberModal from "../components/modals/MemberModal";
import { useGetMemberGaps } from "../api/members";

const MEASURES = [
  { value: "", label: "All Measures" },
  { value: "COL", label: "COL" }, { value: "CBP", label: "CBP" },
  { value: "KED", label: "KED" }, { value: "AMM", label: "AMM" },
  { value: "HBD", label: "HBD" }, { value: "SPC", label: "SPC" },
  { value: "BCS", label: "BCS" }, { value: "OMW", label: "OMW" },
];

export default function MemberGapList() {
  const [measureCode, setMeasureCode] = useState("");
  const [gapStatus, setGapStatus] = useState("");
  const [propensity, setPropensity] = useState("");
  const [page, setPage] = useState(1);
  const [selectedMember, setSelectedMember] = useState<string | null>(null);

  const { data, isLoading } = useGetMemberGaps({ measure_code: measureCode || undefined, gap_status: gapStatus || undefined, propensity: propensity || undefined, page, page_size: 50 });

  const totalPages = data ? Math.ceil(data.total / 50) : 1;

  return (
    <PageShell
      title="Member Gap List"
      subtitle={`${data?.total.toLocaleString() ?? "—"} members with open gaps · H3312`}
    >
      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <select value={measureCode} onChange={e => { setMeasureCode(e.target.value); setPage(1); }}
          className="px-3 py-2 rounded-lg bg-brand-card border border-brand-border text-white text-sm focus:outline-none">
          {MEASURES.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
        </select>
        <select value={gapStatus} onChange={e => { setGapStatus(e.target.value); setPage(1); }}
          className="px-3 py-2 rounded-lg bg-brand-card border border-brand-border text-white text-sm focus:outline-none">
          <option value="">All Gap Types</option>
          <option value="Open">Open</option>
          <option value="Partial">Partial</option>
          <option value="Borderline">Borderline</option>
        </select>
        <select value={propensity} onChange={e => { setPropensity(e.target.value); setPage(1); }}
          className="px-3 py-2 rounded-lg bg-brand-card border border-brand-border text-white text-sm focus:outline-none">
          <option value="">All Propensity</option>
          <option value="high">High &gt;75%</option>
          <option value="medium">Medium 40-75%</option>
          <option value="low">Low &lt;40%</option>
        </select>
      </div>

      {isLoading ? <LoadingSpinner /> : (
        <>
          <div className="card p-0 overflow-hidden">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Member</th><th>Age</th><th>Propensity</th>
                  <th>Measure</th><th>Gap Type</th><th>Last Contact</th>
                  <th>Channel</th><th>PCP</th>
                </tr>
              </thead>
              <tbody>
                {(data?.items ?? []).map(m => (
                  <tr key={m.member_key} className="cursor-pointer" onClick={() => setSelectedMember(m.member_key)}>
                    <td className="text-white font-medium">{m.display_name}</td>
                    <td>{m.age}</td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <div className="w-12 h-1.5 rounded-full bg-slate-700">
                          <div className="h-full rounded-full bg-brand-teal" style={{ width: `${m.propensity_score}%` }} />
                        </div>
                        <span className="text-xs">{m.propensity_score.toFixed(0)}%</span>
                      </div>
                    </td>
                    <td>
                      <div className="text-white text-sm">{m.measure_code}</div>
                      <div className="text-muted text-xs truncate max-w-32">{m.measure_name}</div>
                    </td>
                    <td><StatusBadge status={m.gap_status === "Open" ? "red" : m.gap_status === "Partial" ? "yellow" : "blue"} label={m.gap_status} /></td>
                    <td className="text-muted text-xs">{m.last_contact}</td>
                    <td><ChannelChip channel={m.recommended_channel} /></td>
                    <td className="text-muted text-xs">{m.pcp_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4 text-sm text-muted">
            <span>{data?.total.toLocaleString()} total · page {page} of {totalPages}</span>
            <div className="flex gap-2">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
                className="px-3 py-1 rounded border border-brand-border disabled:opacity-30 hover:text-white">← Prev</button>
              <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}
                className="px-3 py-1 rounded border border-brand-border disabled:opacity-30 hover:text-white">Next →</button>
            </div>
          </div>
        </>
      )}

      <MemberModal memberKey={selectedMember} onClose={() => setSelectedMember(null)} />
    </PageShell>
  );
}
