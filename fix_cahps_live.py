import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# ── 1. Replace iframe with a div for inline rendering ─────────────────────
html = html.replace(
    '<iframe id="cahps-frame" title="CAHPS Overview" style="width:100%;height:100%;border:0;background:#f5f6f8;display:block"></iframe>',
    '<div id="cahps-content" style="width:100%;height:100%;overflow-y:auto;background:#f5f6f8;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif"></div>'
)

# ── 2. Replace the loadCahpsModule function with live renderer ─────────────
OLD_LOAD = re.search(
    r'function loadCahpsModule\(\)\{[\s\S]*?cahpsModuleLoaded = true;\s*\}\s*\}', html
)
if OLD_LOAD:
    NEW_LOAD = r"""function loadCahpsModule(){
  const contractId = window._selectedContractId || 'H3312';
  const contractName = window._selectedContractName || 'Health Plan Advantage Premier';
  renderCahpsLive(contractId, contractName);
}
function renderCahpsLive(contractId, contractName){
  const el = document.getElementById('cahps-content');
  if(!el) return;
  el.innerHTML = '<div style="padding:32px;text-align:center;color:#9ca3af;font-size:13px">Loading CAHPS data...</div>';
  fetch('/api/cahps?contract_id=' + contractId)
    .then(r => r.json())
    .then(data => {
      const composites = data.composites || [];
      const rating = data.current_rating || 0;
      const proj = data.projected_rating || 0;
      const gap = data.gap_to_4_star != null ? data.gap_to_4_star : Math.max(0, 4.0 - proj);
      const days = data.days_remaining || 83;
      const qbp = data.qbp_at_stake || 0;
      const now = new Date();
      const ts = now.toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit'});

      const statusColor = s => s==='ok'?'#166534':s==='risk'?'#92400e':'#991b1b';
      const statusBg = s => s==='ok'?'#dcfce7':s==='risk'?'#fffbeb':'#fef2f2';
      const statusLabel = s => s==='ok'?'ON TRACK':s==='risk'?'AT RISK':'CRITICAL';
      const barColor = s => s==='ok'?'#1D9E75':s==='risk'?'#d97706':'#dc2626';
      const ratingColor = r => r>=4.0?'#166534':r>=3.5?'#d97706':'#dc2626';
      const weightLabel = m => m.weight ? m.weight+'x' : '1x';

      el.innerHTML = `
        <div style="background:#fff;border-bottom:1px solid #e5e7eb;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:48px;flex-shrink:0">
          <div style="display:flex;align-items:center;gap:16px">
            <span style="font-size:14px;font-weight:700">CAHPS Overview</span>
            <span style="font-size:11px;color:#6b7280;padding:0 12px;border-left:1px solid #e5e7eb">Contract ${contractId} &middot; 2025 Measurement Year</span>
            <span style="background:#fef2f2;color:#c0392b;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #fecaca">Star Overview</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#374151">
            <span style="width:8px;height:8px;border-radius:50%;background:#22c55e;display:inline-block"></span>
            <span style="font-weight:600;color:#166534">Live</span>
            <span style="color:#9ca3af">Last updated: ${ts}</span>
          </div>
        </div>
        <div style="padding:24px">
          <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">CAHPS Star Overview</h2>
          <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Where am I bleeding? — Overall star position and composite-level compliance at a glance</p>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px">
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px 20px;text-align:center">
              <div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">Current Rating</div>
              <div style="font-size:32px;font-weight:800;color:${ratingColor(rating)}">${rating} <span style="font-size:24px">★</span></div>
              <div style="font-size:11px;color:#6b7280;margin-top:4px">2025 Official</div>
            </div>
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px 20px;text-align:center">
              <div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">AI Predicted (EOY)</div>
              <div style="font-size:32px;font-weight:800;color:#1D9E75">${proj} <span style="font-size:24px">★</span></div>
              <div style="font-size:11px;color:#6b7280;margin-top:4px">If interventions hold</div>
            </div>
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px 20px;text-align:center">
              <div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">Gap to 4★ Bonus</div>
              <div style="font-size:32px;font-weight:800;color:${gap>0?'#d97706':'#166534'}">${gap>0?'+':''}${gap.toFixed(1)} <span style="font-size:24px">★</span></div>
              <div style="font-size:11px;color:#6b7280;margin-top:4px">~$${(qbp/1000000).toFixed(1)}M QBP at stake</div>
            </div>
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px 20px;text-align:center">
              <div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">Survey Window</div>
              <div style="font-size:32px;font-weight:800;color:#1d4ed8">${days}d</div>
              <div style="font-size:11px;color:#6b7280;margin-top:4px">Feb–Jun 2025</div>
            </div>
          </div>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
            <div style="padding:14px 20px;border-bottom:1px solid #e5e7eb;font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em">
              CAHPS COMPOSITE MEASURES — CLICK ANY ROW TO DEEP DIVE
            </div>
            <table style="width:100%;border-collapse:collapse">
              <thead>
                <tr style="background:#f9fafb;border-bottom:1px solid #e5e7eb">
                  <th style="padding:10px 20px;font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;text-align:left">Measure</th>
                  <th style="padding:10px 16px;font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;text-align:center">Weight</th>
                  <th style="padding:10px 16px;font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;text-align:center">Status</th>
                  <th style="padding:10px 20px;font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;text-align:left">Compliance Score</th>
                </tr>
              </thead>
              <tbody>
                ${composites.sort((a,b)=>a.current_pct-b.current_pct).map(m => `
                  <tr style="border-bottom:1px solid #f3f4f6;cursor:pointer" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background=''">
                    <td style="padding:14px 20px">
                      <div style="font-weight:600;font-size:13px">${m.composite_name || m.composite_code}</div>
                      <div style="font-size:11px;color:#9ca3af;margin-top:2px">${m.composite_code}</div>
                    </td>
                    <td style="padding:14px 16px;text-align:center">
                      <span style="background:#eff6ff;color:#1d4ed8;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700">${weightLabel(m)}</span>
                    </td>
                    <td style="padding:14px 16px;text-align:center">
                      <span style="background:${statusBg(m.status)};color:${statusColor(m.status)};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700">${statusLabel(m.status)}</span>
                    </td>
                    <td style="padding:14px 20px">
                      <div style="display:flex;align-items:center;gap:10px">
                        <div style="flex:1;background:#f3f4f6;border-radius:4px;height:8px;overflow:hidden">
                          <div style="height:100%;width:${Math.round(m.current_pct||0)}%;background:${barColor(m.status)};border-radius:4px"></div>
                        </div>
                        <span style="font-size:14px;font-weight:700;color:${barColor(m.status)};min-width:42px;text-align:right">${Math.round(m.current_pct||0)}%</span>
                      </div>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>`;
    })
    .catch(() => {
      el.innerHTML = '<div style="padding:32px;text-align:center;color:#9ca3af;font-size:13px">Unable to load CAHPS data. Please try again.</div>';
    });
}"""
    html = html[:OLD_LOAD.start()] + NEW_LOAD + html[OLD_LOAD.end():]

# ── 3. Remove the big base64 blob variable (no longer needed) ─────────────
html = re.sub(
    r"const cahpsModuleHtmlB64 = '[A-Za-z0-9+/=\n\r]+';\s*",
    "// cahpsModuleHtmlB64 replaced by live renderCahpsLive()\n",
    html
)

# ── 4. Remove decodeCahpsModule function ──────────────────────────────────
html = re.sub(
    r'function decodeCahpsModule\(\)\{[\s\S]*?return new TextDecoder.*?\}\s*\}',
    '// decodeCahpsModule replaced by renderCahpsLive()',
    html
)

# ── 5. Also update showPage to reload CAHPS when plan changes ─────────────
html = html.replace(
    "if(id==='cahps')loadCahpsModule();",
    "if(id==='cahps'){cahpsModuleLoaded=false;loadCahpsModule();}"
)

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
checks = [
    ('cahps-content', 'cahps-content div'),
    ('renderCahpsLive', 'live renderer function'),
    ('/api/cahps?contract_id=', 'API call'),
    ('composite_name', 'composite name field'),
    ('current_pct', 'compliance score field'),
    ('cahpsModuleHtmlB64', 'base64 blob removed'),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for needle, label in checks:
    found = needle in content
    if label == 'base64 blob removed':
        found = 'PCFET0NUWVBFIGh0bWw' not in content  # first few chars of the blob
    print(f"{'OK' if found else 'MISSING':8s} {label}")
print("Done")
