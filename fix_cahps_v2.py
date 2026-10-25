import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# Replace renderCahpsLive with the full-layout version preserving all tabs
OLD_FN = re.search(r'function renderCahpsLive\(contractId, contractName\)\{[\s\S]*?^\}', html, re.MULTILINE)

NEW_FN = r"""function renderCahpsLive(contractId, contractName){
  const el = document.getElementById('cahps-content');
  if(!el) return;
  el.innerHTML = '<div style="padding:32px;text-align:center;color:#9ca3af;font-size:13px">Loading CAHPS data...</div>';

  // Fetch all needed data in parallel
  Promise.all([
    fetch('/api/cahps?contract_id=' + contractId).then(r=>r.json()).catch(()=>null),
    fetch('/api/interventions').then(r=>r.json()).catch(()=>null),
    fetch('/api/team-view').then(r=>r.json()).catch(()=>null),
  ]).then(([cahps, interventions, teamView]) => {
    const composites = (cahps && cahps.composites) || [];
    const rating = (cahps && cahps.current_rating) || 0;
    const proj = (cahps && cahps.projected_rating) || 0;
    const gap = cahps ? (cahps.gap_to_4_star != null ? cahps.gap_to_4_star : Math.max(0,4.0-proj)) : 0;
    const days = (cahps && cahps.days_remaining) || 83;
    const qbp = (cahps && cahps.qbp_at_stake) || 0;
    const ivItems = Array.isArray(interventions) ? interventions : (interventions && interventions.items) || [];
    const tvItems = Array.isArray(teamView) ? teamView : (teamView && teamView.items) || [];
    const now = new Date();
    const ts = now.toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit'});

    const sColor = s => s==='ok'?'#166534':s==='risk'?'#92400e':'#991b1b';
    const sBg = s => s==='ok'?'#dcfce7':s==='risk'?'#fffbeb':'#fef2f2';
    const sLabel = s => s==='ok'?'ON TRACK':s==='risk'?'AT RISK':'CRITICAL';
    const barClr = s => s==='ok'?'#1D9E75':s==='risk'?'#d97706':'#dc2626';
    const rClr = r => r>=4.0?'#166534':r>=3.5?'#d97706':'#dc2626';

    function tabBtn(id, label, active) {
      return `<button onclick="cahpsTab('${id}',this)" style="padding:0 16px;height:48px;border:none;background:none;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid ${active?'#c0392b':'transparent'};color:${active?'#c0392b':'#6b7280'}" id="ctab-${id}">${label}</button>`;
    }

    el.innerHTML = `
      <style>
        .cahps-tab-pane{display:none}.cahps-tab-pane.active{display:block}
        .cahps-row:hover{background:#f9fafb!important}
        .iv-row{border-bottom:1px solid #f3f4f6;padding:14px 20px;display:grid;grid-template-columns:1fr auto auto;gap:16px;align-items:center}
        .tv-row{border-bottom:1px solid #f3f4f6;padding:12px 20px;display:grid;grid-template-columns:1fr 80px 80px 80px auto;gap:12px;align-items:center}
      </style>
      <div style="background:#fff;border-bottom:1px solid #e5e7eb;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:48px;flex-shrink:0;position:sticky;top:0;z-index:10">
        <div style="display:flex;align-items:center;gap:0">
          <span style="font-size:13px;font-weight:700;color:#111;padding-right:16px;border-right:1px solid #e5e7eb;margin-right:4px">CAHPS Overview</span>
          <span style="font-size:11px;color:#6b7280;padding:0 16px;border-right:1px solid #e5e7eb">Contract ${contractId} &middot; 2025 Measurement Year</span>
          ${tabBtn('star','Star Overview',true)}
          ${tabBtn('pulse','Pulse Surveys',false)}
          ${tabBtn('iv','Intervention Hub',false)}
          ${tabBtn('tv','Team View',false)}
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:12px">
          <span style="width:7px;height:7px;border-radius:50%;background:#22c55e;display:inline-block"></span>
          <span style="font-weight:600;color:#166534">Live</span>
          <span style="color:#9ca3af;font-size:11px">Last updated: ${ts}</span>
        </div>
      </div>

      <!-- TAB: Star Overview -->
      <div id="ctab-pane-star" class="cahps-tab-pane active" style="padding:24px">
        <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">CAHPS Star Overview</h2>
        <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Where am I bleeding? — Overall star position and composite-level compliance at a glance</p>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px">
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Current Rating</div>
            <div style="font-size:30px;font-weight:800;color:${rClr(rating)}">${rating}★</div>
            <div style="font-size:11px;color:#6b7280;margin-top:3px">2025 Official</div>
          </div>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">AI Predicted (EOY)</div>
            <div style="font-size:30px;font-weight:800;color:#1D9E75">${proj.toFixed(2)}★</div>
            <div style="font-size:11px;color:#6b7280;margin-top:3px">If interventions hold</div>
          </div>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Gap to 4★ Bonus</div>
            <div style="font-size:30px;font-weight:800;color:${gap>0?'#d97706':'#166534'}">${gap>0?'+':''}${gap.toFixed(1)}★</div>
            <div style="font-size:11px;color:#6b7280;margin-top:3px">~$${(qbp/1000000).toFixed(1)}M QBP at stake</div>
          </div>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;text-align:center">
            <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Survey Window</div>
            <div style="font-size:30px;font-weight:800;color:#1d4ed8">${days}d</div>
            <div style="font-size:11px;color:#6b7280;margin-top:3px">Feb–Jun 2025</div>
          </div>
        </div>
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
          <div style="padding:12px 20px;border-bottom:1px solid #e5e7eb;font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em">CAHPS COMPOSITE MEASURES — CLICK ANY ROW TO DEEP DIVE</div>
          <div style="display:grid;grid-template-columns:1fr 80px 110px 1fr;padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb">
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Measure</span>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Weight</span>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Status</span>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Compliance Score</span>
          </div>
          ${composites.sort((a,b)=>a.current_pct-b.current_pct).map(m=>`
            <div class="cahps-row" style="display:grid;grid-template-columns:1fr 80px 110px 1fr;padding:14px 20px;border-bottom:1px solid #f9fafb;cursor:pointer">
              <div>
                <div style="font-weight:600;font-size:13px">${m.composite_name||m.composite_code}</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:1px">${m.composite_code}</div>
              </div>
              <div style="text-align:center;align-self:center">
                <span style="background:#eff6ff;color:#1d4ed8;padding:3px 9px;border-radius:6px;font-size:11px;font-weight:700">${m.weight||1}×</span>
              </div>
              <div style="text-align:center;align-self:center">
                <span style="background:${sBg(m.status)};color:${sColor(m.status)};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700">${sLabel(m.status)}</span>
              </div>
              <div style="display:flex;align-items:center;gap:10px;align-self:center">
                <div style="flex:1;background:#f3f4f6;border-radius:4px;height:8px;overflow:hidden">
                  <div style="height:100%;width:${Math.round(m.current_pct||0)}%;background:${barClr(m.status)};border-radius:4px"></div>
                </div>
                <span style="font-size:14px;font-weight:700;color:${barClr(m.status)};min-width:40px;text-align:right">${Math.round(m.current_pct||0)}%</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- TAB: Pulse Surveys -->
      <div id="ctab-pane-pulse" class="cahps-tab-pane" style="padding:24px">
        <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">Pulse Surveys</h2>
        <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Real-time member satisfaction pulse data by composite</p>
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
          <div style="padding:12px 20px;border-bottom:1px solid #e5e7eb;font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em">Composite Pulse Scores</div>
          ${composites.map(m=>`
            <div style="padding:14px 20px;border-bottom:1px solid #f9fafb;display:grid;grid-template-columns:1fr 120px 200px;gap:16px;align-items:center">
              <div>
                <div style="font-weight:600;font-size:13px">${m.composite_name||m.composite_code}</div>
                <div style="font-size:11px;color:#9ca3af">${m.composite_code}</div>
              </div>
              <div style="text-align:center">
                <span style="font-size:18px;font-weight:800;color:${barClr(m.status)}">${Math.round(m.current_pct||0)}%</span>
                <div style="font-size:10px;color:#9ca3af;margin-top:2px">Top-box rate</div>
              </div>
              <div>
                <div style="background:#f3f4f6;border-radius:4px;height:10px;overflow:hidden">
                  <div style="height:100%;width:${Math.round(m.current_pct||0)}%;background:${barClr(m.status)};border-radius:4px"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:10px;color:#9ca3af;margin-top:3px"><span>0%</span><span>Target 80%</span><span>100%</span></div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- TAB: Intervention Hub -->
      <div id="ctab-pane-iv" class="cahps-tab-pane" style="padding:24px">
        <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">Intervention Hub</h2>
        <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Active and planned interventions driving CAHPS improvement</p>
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
          <div style="padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb;display:grid;grid-template-columns:1fr auto auto;gap:16px">
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Intervention</span>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Lift</span>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Status</span>
          </div>
          ${ivItems.length ? ivItems.map(iv=>{
            const stCl = iv.intervention_status==='Active'?'#166534':iv.intervention_status==='Planned'?'#1d4ed8':'#6b7280';
            const stBg = iv.intervention_status==='Active'?'#dcfce7':iv.intervention_status==='Planned'?'#eff6ff':'#f3f4f6';
            return `<div class="iv-row">
              <div>
                <div style="font-weight:600;font-size:13px">${iv.intervention_name||''}</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:2px">${iv.owner_department||''} &middot; Due ${iv.due_date||''} &middot; ${(iv.target_member_count||0).toLocaleString()} members</div>
              </div>
              <span style="font-size:14px;font-weight:700;color:#1D9E75;text-align:center">+${iv.expected_lift_pct||0}%</span>
              <span style="background:${stBg};color:${stCl};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700">${iv.intervention_status||'—'}</span>
            </div>`;
          }).join('') : '<div style="padding:32px;text-align:center;color:#9ca3af">No interventions found</div>'}
        </div>
      </div>

      <!-- TAB: Team View -->
      <div id="ctab-pane-tv" class="cahps-tab-pane" style="padding:24px">
        <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">Team View</h2>
        <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Care team performance and measure ownership</p>
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
          <div style="padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb;display:grid;grid-template-columns:1fr 80px 80px 80px auto;gap:12px">
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Department / Leader</span>
            <span style="font-size:10px;font-weight:700;color:#1D9E75;text-transform:uppercase;text-align:center">On Track</span>
            <span style="font-size:10px;font-weight:700;color:#d97706;text-transform:uppercase;text-align:center">At Risk</span>
            <span style="font-size:10px;font-weight:700;color:#dc2626;text-transform:uppercase;text-align:center">Critical</span>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Next Action</span>
          </div>
          ${tvItems.length ? tvItems.map(t=>`
            <div class="tv-row">
              <div>
                <div style="font-weight:600;font-size:13px">${t.department||''}</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:1px">${t.team_leader||''}</div>
              </div>
              <span style="text-align:center;font-size:16px;font-weight:800;color:#1D9E75">${t.on_track_count||0}</span>
              <span style="text-align:center;font-size:16px;font-weight:800;color:#d97706">${t.at_risk_count||0}</span>
              <span style="text-align:center;font-size:16px;font-weight:800;color:#dc2626">${t.critical_count||0}</span>
              <span style="font-size:11px;color:#374151">${t.next_action||'—'}</span>
            </div>
          `).join('') : '<div style="padding:32px;text-align:center;color:#9ca3af">No team data found</div>'}
        </div>
      </div>
    `;

    // Wire tab buttons
    window.cahpsTab = function(id, btn) {
      el.querySelectorAll('.cahps-tab-pane').forEach(p=>p.classList.remove('active'));
      el.querySelectorAll('button[id^="ctab-"]').forEach(b=>{
        b.style.borderBottomColor='transparent';b.style.color='#6b7280';
      });
      const pane = el.querySelector('#ctab-pane-'+id);
      if(pane) pane.classList.add('active');
      if(btn){btn.style.borderBottomColor='#c0392b';btn.style.color='#c0392b';}
    };
  });
}"""

if OLD_FN:
    html = html[:OLD_FN.start()] + NEW_FN + html[OLD_FN.end():]
    print("Replaced renderCahpsLive")
else:
    print("ERROR: renderCahpsLive not found")

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify tabs exist
checks = ['Star Overview','Pulse Surveys','Intervention Hub','Team View',
          "fetch('/api/interventions')", "fetch('/api/team-view')"]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for c in checks:
    print(f"{'OK' if c in content else 'MISSING':8s} {c}")
print("Done")
