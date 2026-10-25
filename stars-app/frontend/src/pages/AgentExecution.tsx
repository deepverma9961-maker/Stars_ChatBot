import { useState } from "react";
import PageShell from "../components/layout/PageShell";
import ChannelChip from "../components/shared/ChannelChip";
import { useGetMemberGaps } from "../api/members";

const WEEKS = [
  { label: "Week 1", desc: "High propensity · First contact" },
  { label: "Week 2", desc: "Non-responders + incentive" },
  { label: "Week 3", desc: "Hard cases · PCP alerts" },
  { label: "Week 4", desc: "Final sweep · Snapshot prep" },
];

const CHANNELS = ["Call", "SMS", "Email"] as const;

export default function AgentExecution() {
  const [activeWeek, setActiveWeek] = useState(0);
  const [activeChannel, setActiveChannel] = useState<"Call" | "SMS" | "Email">("Call");
  const [selectedMember, setSelectedMember] = useState<string | null>(null);

  const { data } = useGetMemberGaps({ contract_id: "H3312", page_size: 30 });
  const members = data?.items ?? [];

  const member = members.find(m => m.member_key === selectedMember);

  return (
    <PageShell title="Agent Execution" subtitle="Weekly outreach queues · H3312 · PY2025">
      <div className="flex gap-4 h-[calc(100vh-140px)]">
        {/* Week sidebar */}
        <div className="w-44 flex-shrink-0 space-y-2">
          {WEEKS.map((w, i) => (
            <div
              key={i}
              onClick={() => setActiveWeek(i)}
              className={`card cursor-pointer transition ${activeWeek === i ? "border-brand-red" : ""}`}
            >
              <div className={`font-semibold text-sm ${activeWeek === i ? "text-brand-red" : "text-white"}`}>{w.label}</div>
              <div className="text-muted text-xs mt-0.5">{w.desc}</div>
            </div>
          ))}
        </div>

        {/* Main */}
        <div className="flex-1 flex gap-4 min-w-0">
          {/* Queue */}
          <div className="flex-1 flex flex-col min-w-0">
            {/* Channel tabs */}
            <div className="flex gap-2 mb-3">
              {CHANNELS.map(ch => (
                <button
                  key={ch}
                  onClick={() => setActiveChannel(ch)}
                  className={`fchip ${activeChannel === ch ? "teal" : ""}`}
                >
                  {ch} Queue
                </button>
              ))}
            </div>

            <div className="card flex-1 overflow-y-auto p-0">
              <div className="px-4 py-3 border-b border-brand-border flex items-center justify-between">
                <div className="text-sm font-medium text-white">{WEEKS[activeWeek].label} · <ChannelChip channel={activeChannel} /></div>
                <span className="text-xs text-muted">{members.length} members</span>
              </div>
              {members.map(m => (
                <div
                  key={m.member_key}
                  onClick={() => setSelectedMember(m.member_key === selectedMember ? null : m.member_key)}
                  className={`px-4 py-3 border-b border-brand-border/40 cursor-pointer flex items-center justify-between hover:bg-white/3 transition ${selectedMember === m.member_key ? "bg-white/5" : ""}`}
                >
                  <div>
                    <div className="text-white text-sm font-medium">{m.display_name}</div>
                    <div className="text-muted text-xs">{m.measure_name} · {m.gap_status}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-brand-teal">{m.propensity_score.toFixed(0)}%</div>
                    <div className="text-muted text-xs">propensity</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Detail panel */}
          {member ? (
            <div className="w-72 flex-shrink-0 card overflow-y-auto">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-brand-red flex items-center justify-center text-white font-bold">
                  {member.display_name[0]}
                </div>
                <div>
                  <div className="font-semibold text-white">{member.display_name}</div>
                  <div className="text-muted text-xs">Age {member.age}</div>
                </div>
              </div>

              {[
                ["Gap", member.measure_name],
                ["Status", member.gap_status],
                ["Last Contact", member.last_contact],
                ["PCP", member.pcp_name],
                ["Channel", member.recommended_channel],
                ["Propensity", `${member.propensity_score.toFixed(0)}%`],
              ].map(([k, v]) => (
                <div key={k} className="supp-row text-sm">
                  <span className="text-muted">{k}</span>
                  <span className="text-white">{v}</span>
                </div>
              ))}

              <div className="mt-4 p-3 rounded-lg bg-brand-dark border border-brand-border text-xs text-slate-300">
                <div className="font-medium text-white mb-1">Outreach Script</div>
                "Hello, may I speak with {member.display_name.split(" ")[0]}? This is a courtesy call regarding your {member.measure_name.split("–")[0]} care gap. We'd like to help schedule an appointment..."
              </div>

              <div className="flex gap-2 mt-3">
                <button className="flex-1 px-3 py-2 rounded-lg bg-brand-teal text-white text-xs font-medium hover:opacity-90">Log Contact</button>
                <button className="flex-1 px-3 py-2 rounded-lg border border-brand-border text-white text-xs hover:bg-white/5">Close Gap</button>
              </div>
            </div>
          ) : (
            <div className="w-72 flex-shrink-0 card flex items-center justify-center text-muted text-sm">
              Select a member to view details
            </div>
          )}
        </div>
      </div>
    </PageShell>
  );
}
