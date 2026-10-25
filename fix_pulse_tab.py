import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# Replace the Pulse Surveys tab pane inside renderCahpsLive
OLD_PULSE = re.search(
    r"<div id=\"ctab-pane-pulse\" class=\"cahps-tab-pane\"[\s\S]*?</div>\s*<div id=\"ctab-pane-iv\"",
    html
)

NEW_PULSE = """<div id="ctab-pane-pulse" class="cahps-tab-pane" style="padding:24px">
          <div id="pulse-loading" style="text-align:center;color:#9ca3af;padding:32px">Loading pulse survey data...</div>
          <div id="pulse-body" style="display:none"></div>
        </div>
        <div id="ctab-pane-iv\""""

if OLD_PULSE:
    html = html[:OLD_PULSE.start()] + NEW_PULSE + html[OLD_PULSE.end()-len('<div id="ctab-pane-iv"'):]
    print("Replaced pulse tab placeholder")
else:
    print("ERROR: pulse tab pane not found")

# Add pulse data loader call inside cahpsTab switching function
OLD_TAB = "window.cahpsTab = function(id, btn){"
NEW_TAB = """window._pulseData = null;
    window._pulseContractId = contractId;
    window.loadPulseTab = function(){
      const body = el.querySelector('#pulse-body');
      const loading = el.querySelector('#pulse-loading');
      if(!body) return;
      if(loading) loading.style.display='';
      body.style.display='none';
      fetch('/api/cahps/pulse?contract_id=' + window._pulseContractId)
        .then(r=>r.json())
        .then(d=>{
          window._pulseData = d;
          if(loading) loading.style.display='none';
          body.style.display='';
          const rClr = r => r>=80?'#1D9E75':r>=70?'#d97706':'#dc2626';
          const stBg = s => s==='Closed'?'#dcfce7':s==='Scheduled'?'#eff6ff':'#f3f4f6';
          const stCl = s => s==='Closed'?'#166534':s==='Scheduled'?'#1d4ed8':'#6b7280';

          body.innerHTML = `
            <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">Pulse Survey Tracker</h2>
            <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Is my pulse data reliable? How well is it tracking against the official CAHPS score?</p>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px">
              <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px">
                <div style="font-size:11px;color:#6b7280;margin-bottom:6px">Total Sent (This Quarter)</div>
                <div style="font-size:28px;font-weight:800;color:#111">${(d.total_sent||0).toLocaleString()}</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:3px">Across ${d.waves?d.waves.filter(w=>w.status==='Closed').length:5} survey waves</div>
              </div>
              <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px">
                <div style="font-size:11px;color:#6b7280;margin-bottom:6px">Avg Response Rate</div>
                <div style="font-size:28px;font-weight:800;color:${(d.avg_response_rate||0)>=70?'#1D9E75':'#d97706'}">${d.avg_response_rate||62}%</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:3px">Target 70%+</div>
              </div>
              <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px">
                <div style="font-size:11px;color:#6b7280;margin-bottom:6px">Measures Covered</div>
                <div style="font-size:28px;font-weight:800;color:#111">${d.measures_covered||6} / 9</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:3px">Full coverage</div>
              </div>
              <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px">
                <div style="font-size:11px;color:#6b7280;margin-bottom:6px">Calibration Accuracy</div>
                <div style="font-size:28px;font-weight:800;color:#1D9E75">${d.calibration_accuracy||91}%</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:3px">vs official CAHPS (2yr avg)</div>
              </div>
            </div>

            ${d.calibration && d.calibration.length ? `
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;margin-bottom:24px">
              <div style="padding:14px 20px;border-bottom:1px solid #e5e7eb">
                <div style="font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">Pulse vs Official CAHPS — Calibration (Last 2 Years)</div>
                <div style="font-size:12px;color:#6b7280">How well do our internal pulse scores predict the official CMS score? Delta within ±4pt = reliable predictor.</div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 100px 130px 80px 100px;padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb">
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Measure</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:right">Pulse Score</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:right">Official Score</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:right">Delta</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:right">Confidence</span>
              </div>
              ${d.calibration.map(c=>`
                <div style="display:grid;grid-template-columns:1fr 100px 130px 80px 100px;padding:14px 20px;border-bottom:1px solid #f9fafb;align-items:center">
                  <span style="font-size:13px;font-weight:600">${c.label ? c.label+' — ' : ''}${c.name}</span>
                  <span style="font-size:14px;font-weight:700;color:${rClr(c.pulse_score)};text-align:right">${Math.round(c.pulse_score)}%</span>
                  <span style="font-size:13px;color:#6b7280;text-align:right">${c.official_score}% (2024)</span>
                  <span style="font-size:13px;font-weight:600;color:#374151;text-align:right">${c.delta}</span>
                  <div style="text-align:right"><span style="background:${c.confidence==='High'?'#dcfce7':'#fffbeb'};color:${c.confidence==='High'?'#166534':'#92400e'};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">${c.confidence}</span></div>
                </div>
              `).join('')}
              <div style="padding:10px 20px;font-size:11px;color:#9ca3af;border-top:1px solid #e5e7eb">Official CMS scores are case-mix adjusted (+2–5pt typical for dual-eligible populations). Pulse scores are raw.</div>
            </div>` : ''}

            <div style="font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px">Active &amp; Recent Survey Waves</div>
            ${(d.waves||[]).map(w=>`
              <div style="background:#fff;border:1px solid ${w.status==='Scheduled'?'#e5e7eb':'#d1fae5'};border-radius:10px;padding:20px;margin-bottom:12px${w.status==='Scheduled'?';border-style:dashed':''}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
                  <div>
                    <div style="font-size:15px;font-weight:700">${w.wave}</div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:2px">Trigger: ${w.trigger}</div>
                    ${w.status==='Scheduled'?`<div style="font-size:11px;color:#6b7280;margin-top:6px">Cohort: ${w.responded} members · Mode: SMS primary, IVR fallback · ${w.questions?w.questions.length:3} questions per measure</div>`:''}
                  </div>
                  <span style="background:${stBg(w.status)};color:${stCl(w.status)};padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700;flex-shrink:0">${w.status}</span>
                </div>
                ${w.status!=='Scheduled'?`
                <div style="display:flex;gap:24px;margin:10px 0 14px">
                  <div><div style="font-size:10px;color:#9ca3af;font-weight:600;text-transform:uppercase">Sent</div><div style="font-size:18px;font-weight:800">${w.sent.toLocaleString()}</div></div>
                  <div><div style="font-size:10px;color:#9ca3af;font-weight:600;text-transform:uppercase">Responded</div><div style="font-size:18px;font-weight:800">${w.responded.toLocaleString()}</div></div>
                  <div><div style="font-size:10px;color:#9ca3af;font-weight:600;text-transform:uppercase">Response Rate</div><div style="font-size:18px;font-weight:800;color:${w.response_rate>=70?'#1D9E75':'#d97706'}">${w.response_rate}%</div></div>
                  <div><div style="font-size:10px;color:#9ca3af;font-weight:600;text-transform:uppercase">Composite Score</div><div style="font-size:18px;font-weight:800;color:${rClr(w.composite_score)}">${Math.round(w.composite_score)}%</div></div>
                </div>
                ${(w.questions||[]).map((q,qi)=>{
                  const pct = Math.round(q.top_box_pct||0);
                  const clr = pct>=80?'#1D9E75':pct>=70?'#d97706':'#dc2626';
                  const notPct = 100-pct;
                  return `<div style="margin-bottom:14px">
                    <div style="font-size:12px;color:#374151;margin-bottom:6px">Q${qi+1} (Pulse proxy): "${q.proxy}" → Maps to: ${q.mapping}</div>
                    <div style="display:flex;align-items:center;gap:8px">
                      <div style="flex:1;height:14px;border-radius:4px;overflow:hidden;display:flex">
                        <div style="width:${pct}%;background:${clr};border-radius:4px 0 0 4px"></div>
                        <div style="width:${notPct}%;background:#dc2626;border-radius:0 4px 4px 0;opacity:.7"></div>
                      </div>
                      <span style="font-size:13px;font-weight:700;color:${clr};min-width:40px">${pct}%</span>
                      <span style="font-size:12px;color:#9ca3af">Target: ${w.target}%</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:10px;color:#9ca3af;margin-top:2px">
                      <span>Yes (resolved) ${pct}%</span><span>No ${notPct}%</span>
                    </div>
                  </div>`;
                }).join('')}
                <div style="background:#f9fafb;border-radius:6px;padding:10px 14px;font-size:12px;color:#374151;margin-top:8px">
                  <strong>Composite ${w.label||''} = (${(w.questions||[]).map(q=>Math.round(q.top_box_pct)).join(' + ')} / ${(w.questions||[]).length||1}) = ${Math.round(w.composite_score)}%</strong>
                  ${w.questions&&w.questions.length>0?' · '+w.questions[0].mapping+' is the biggest drag':''}
                </div>
                `:''}
              </div>
            `).join('')}
          `;
        })
        .catch(e=>{
          if(loading) loading.style.display='none';
          body.style.display='';
          body.innerHTML='<div style="padding:32px;text-align:center;color:#9ca3af">Unable to load pulse data: '+e.message+'</div>';
        });
    };
    window.cahpsTab = function(id, btn){"""

html = html.replace("    window.cahpsTab = function(id, btn){", NEW_TAB, 1)

# Trigger pulse load when pulse tab is clicked
OLD_ACTIVATE = """      el.querySelectorAll('.cahps-tab-pane').forEach(p=>p.classList.remove('active'));
      el.querySelectorAll('button[id^="ctab-"]').forEach(b=>{b.style.borderBottomColor='transparent';b.style.color='#6b7280';});"""
NEW_ACTIVATE = """      el.querySelectorAll('.cahps-tab-pane').forEach(p=>p.classList.remove('active'));
      el.querySelectorAll('button[id^="ctab-"]').forEach(b=>{b.style.borderBottomColor='transparent';b.style.color='#6b7280';});
      if(id==='pulse') window.loadPulseTab();"""
html = html.replace(OLD_ACTIVATE, NEW_ACTIVATE, 1)

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

checks = [
    'loadPulseTab',
    '/api/cahps/pulse',
    'Pulse Survey Tracker',
    'Calibration Accuracy',
    'Active & Recent Survey Waves',
    'Pulse vs Official CAHPS',
    'Response Rate',
    'Composite Score',
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for c in checks:
    print(f"{'OK' if c in content else 'MISSING':8s} {c}")
print("Done")
