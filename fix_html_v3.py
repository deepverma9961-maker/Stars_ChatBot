import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# ── 1. Inject data-source status badge CSS + HTML after <body> ────────────
BADGE_CSS = """
<style>
#data-source-badge{position:fixed;bottom:16px;right:16px;z-index:9999;display:flex;align-items:center;gap:6px;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:.03em;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.15);transition:all .3s;user-select:none}
#data-source-badge.loading{background:#f3f4f6;color:#6b7280;border:1px solid #e5e7eb}
#data-source-badge.live{background:#dcfce7;color:#166534;border:1px solid #86efac}
#data-source-badge.fallback{background:#fef2f2;color:#b91c1c;border:1px solid #fecaca}
#data-source-badge .ds-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
#data-source-badge.loading .ds-dot{background:#9ca3af;animation:pulse 1.5s infinite}
#data-source-badge.live .ds-dot{background:#22c55e}
#data-source-badge.fallback .ds-dot{background:#ef4444;animation:pulse 2s infinite}
#data-source-tooltip{position:fixed;bottom:50px;right:16px;z-index:9998;background:#1f2937;color:#f9fafb;font-size:11px;padding:8px 12px;border-radius:8px;max-width:260px;line-height:1.5;display:none;box-shadow:0 4px 12px rgba(0,0,0,.3)}
#data-source-badge:hover + #data-source-tooltip{display:block}
</style>
"""

BADGE_HTML = """
<div id="data-source-badge" class="loading" title="Data source status">
  <span class="ds-dot"></span>
  <span id="ds-label">Connecting...</span>
</div>
<div id="data-source-tooltip">Checking Databricks connection...</div>
"""

# Insert badge CSS before </style> first occurrence after <head>
html = html.replace('</style>', BADGE_CSS + '</style>', 1)

# Insert badge HTML right after <body> or before first <div>
if '<body>' in html:
    html = html.replace('<body>', '<body>' + BADGE_HTML, 1)
else:
    # Insert before first div
    html = html.replace('<div', BADGE_HTML + '<div', 1)

# ── 2. Add connection check to initApp() ──────────────────────────────────
STATUS_CHECK = """
  // ── Connection status badge ─────────────────────────────────────────────
  const badge=document.getElementById('data-source-badge');
  const dsLabel=document.getElementById('ds-label');
  const tooltip=document.getElementById('data-source-tooltip');
  try{
    const cs=await fetch('/api/connection-status').then(r=>r.json());
    if(cs.connected&&cs.source==='live'){
      if(badge){badge.className='';badge.classList.add('live');}
      if(dsLabel)dsLabel.textContent='LIVE DATA';
      if(tooltip)tooltip.textContent='Connected to Databricks. '+cs.row_count+' plan rows loaded from gold tables.';
    }else{
      if(badge){badge.className='';badge.classList.add('fallback');}
      if(dsLabel)dsLabel.textContent='STATIC DATA';
      if(tooltip)tooltip.textContent='Databricks unavailable. Showing built-in reference data. Reason: '+(cs.reason||'unknown');
    }
  }catch(e){
    if(badge){badge.className='';badge.classList.add('fallback');}
    if(dsLabel)dsLabel.textContent='STATIC DATA';
    if(tooltip)tooltip.textContent='Could not reach API. Showing built-in reference data.';
  }
"""

# Insert at the START of initApp(), right after the opening brace
html = html.replace(
    'async function initApp(){\n  // ── Star summary KPIs',
    'async function initApp(){\n' + STATUS_CHECK + '\n  // ── Star summary KPIs'
)

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
checks = [
    ('data-source-badge', 'badge element'),
    ('ds-label', 'label span'),
    ('data-source-tooltip', 'tooltip'),
    ('/api/connection-status', 'connection-status fetch'),
    ('LIVE DATA', 'live label'),
    ('STATIC DATA', 'static label'),
    ('Connecting...', 'loading state'),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for needle, label in checks:
    print(f"{'OK' if needle in content else 'MISSING':8s} {label}")
print("Done")
