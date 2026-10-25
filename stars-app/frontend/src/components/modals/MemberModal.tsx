import { useState } from "react";
import { useGetMemberProfile } from "../../api/members";
import LoadingSpinner from "../shared/LoadingSpinner";
import StatusBadge from "../shared/StatusBadge";
import ChannelChip from "../shared/ChannelChip";

const TABS = ["Overview", "Clinical", "Medications", "Measures", "Claims"];

interface MemberModalProps {
  memberKey: string | null;
  onClose: () => void;
}

export default function MemberModal({ memberKey, onClose }: MemberModalProps) {
  const [tab, setTab] = useState("Overview");
  const { data, isLoading } = useGetMemberProfile(memberKey);

  if (!memberKey) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-brand-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-brand-red flex items-center justify-center text-white font-bold">
              {data?.display_name?.[0] ?? "?"}
            </div>
            <div>
              <div className="font-semibold text-white">{data?.display_name ?? "Loading..."}</div>
              <div className="text-muted text-xs">
                {data ? `Age ${data.age} · ${data.plan_name}` : memberKey}
              </div>
            </div>
          </div>
          <button onClick={onClose} className="text-muted hover:text-white text-xl leading-none">✕</button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-brand-border px-4">
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)} className={`mtab ${tab === t ? "active" : ""}`}>{t}</button>
          ))}
        </div>

        {/* Body */}
        <div className="p-6">
          {isLoading ? (
            <LoadingSpinner />
          ) : data ? (
            <>
              {tab === "Overview" && (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {[
                    ["Contract", data.contract_id],
                    ["Utilization Segment", data.utilization_segment],
                    ["Dual Eligible", data.dual_eligible ? "Yes" : "No"],
                    ["LIS Status", data.lis_flag ? "Yes" : "No"],
                    ["Gender", data.gender],
                    ["Propensity Score", `${data.propensity_score.toFixed(0)}%`],
                  ].map(([k, v]) => (
                    <div key={k} className="card">
                      <div className="text-muted text-xs">{k}</div>
                      <div className="text-white font-medium mt-1">{v}</div>
                    </div>
                  ))}
                </div>
              )}

              {tab === "Clinical" && (
                <div className="space-y-2">
                  {data.clinical_events.map((e, i) => (
                    <div key={i} className="card flex items-start gap-3">
                      <div className="text-xs text-muted whitespace-nowrap mt-0.5">{e.event_date}</div>
                      <div>
                        <div className="text-white text-sm font-medium">{e.description}</div>
                        <div className="text-muted text-xs">{e.event_type} · {e.provider}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {tab === "Medications" && (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Drug</th><th>Days Supply</th><th>Last Fill</th><th>Adherent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.medications.map((m, i) => (
                      <tr key={i}>
                        <td className="text-white">{m.drug_name}</td>
                        <td>{m.days_supply}d</td>
                        <td>{m.last_fill}</td>
                        <td><StatusBadge status={m.adherent ? "green" : "red"} label={m.adherent ? "Yes" : "No"} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {tab === "Measures" && (
                <div className="space-y-2">
                  {data.open_gaps.map((g, i) => (
                    <div key={i} className="card flex items-center justify-between gap-3">
                      <div>
                        <div className="text-white text-sm font-medium">{g.measure_name}</div>
                        <div className="text-muted text-xs">{g.measure_code}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <StatusBadge status={g.gap_status === "Open" ? "red" : g.gap_status === "Partial" ? "yellow" : "blue"} label={g.gap_status} />
                        <ChannelChip channel={g.recommended_channel} />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {tab === "Claims" && (
                <div className="text-muted text-sm text-center py-8">
                  Claims history requires Databricks SQL access.<br />
                  Connect to see full claims & Rx transaction detail.
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
