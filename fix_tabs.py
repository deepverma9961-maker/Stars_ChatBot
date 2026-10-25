import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# ── 1. Remove HPR intervention from IV_DATA ────────────────────────────────
OLD_HPR = """,
        {composite_code:'HPR',composite_label:'Overall Plan Rating',composite_name:'Overall Plan Rating',
         name:'Implement structured service recovery programme triggered by negative NLP sentiment',owner:'Member Experience',
         to:'Member Experience Director',send_to:'Member Experience Director',send_email:'memberexp.director@healthplan.com',
         metric:'Service recovery contact rate',current_val:'46%',target_val:'≥90%',status:'In Progress',
         headline:'Only 46% of members who express negative sentiment receive a structured service recovery outreach. This is the primary driver of low overall plan ratings.',
         wrong_metrics:['Service recovery contact rate: 46% (target ≥90%)','NPS: 28 (target ≥45)','Member retention rate: 84% (target ≥92%)','Voluntary disenrollment rate: 6.2% (target ≤4%)'],
         action:'Deploy NLP pipeline to flag all negative-sentiment interactions (calls, surveys, portal messages). Trigger 48h service recovery outreach with dedicated concierge team.',
         done:'Service recovery contact rate ≥90% within 48h for all flagged negative-sentiment interactions'},"""
html = html.replace(OLD_HPR, '', 1)

# ── 2. Fix tab switching to be smooth with caching ─────────────────────────
# Replace loadPulseTab to check cache first
OLD_PULSE_LOAD = """    window.loadPulseTab = function(){
      const body = el.querySelector('#pulse-body');
      const loading = el.querySelector('#pulse-loading');
      if(!body) return;
      if(loading) loading.style.display='';
      body.style.display='none';
      fetch('/api/cahps/pulse?contract_id=' + window._pulseContractId)"""

NEW_PULSE_LOAD = """    window.loadPulseTab = function(){
      const body = el.querySelector('#pulse-body');
      const loading = el.querySelector('#pulse-loading');
      if(!body) return;
      // If already loaded, just show — no flicker
      if(window._pulseLoaded){body.style.display='';if(loading)loading.style.display='none';return;}
      if(loading) loading.style.display='';
      body.style.display='none';
      fetch('/api/cahps/pulse?contract_id=' + window._pulseContractId)"""

html = html.replace(OLD_PULSE_LOAD, NEW_PULSE_LOAD, 1)

# Mark pulse as loaded after data renders
OLD_PULSE_END = "        .catch(e=>{"
# Find the catch inside loadPulseTab specifically
PULSE_SECTION_START = html.find("window.loadPulseTab = function()")
PULSE_CATCH_POS = html.find("        .catch(e=>{", PULSE_SECTION_START)
# Insert _pulseLoaded = true; before the catch
html = html[:PULSE_CATCH_POS] + "        window._pulseLoaded = true;\n" + html[PULSE_CATCH_POS:]

# ── 3. Fix IV tab to cache similarly ──────────────────────────────────────
OLD_IV_LOAD = """    window.loadIvTab = function(composites){
      const body = document.getElementById('iv-body');
      const loading = document.getElementById('iv-loading');
      if(!body) return;
      if(loading) loading.style.display='none';
      body.style.display='';"""

NEW_IV_LOAD = """    window.loadIvTab = function(composites){
      const body = document.getElementById('iv-body');
      const loading = document.getElementById('iv-loading');
      if(!body) return;
      // If already loaded, just show — no flicker
      if(window._ivLoaded){body.style.display='';if(loading)loading.style.display='none';return;}
      window._ivLoaded = true;
      if(loading) loading.style.display='none';
      body.style.display='';"""

html = html.replace(OLD_IV_LOAD, NEW_IV_LOAD, 1)

# ── 4. Fix main cahpsTab switching — ensure smooth hide/show ──────────────
# Replace the existing cahpsTab body to be smoother
OLD_CAHPS_TAB_BODY = """      el.querySelectorAll('.cahps-tab-pane').forEach(p=>p.classList.remove('active'));
      el.querySelectorAll('button[id^="ctab-"]').forEach(b=>{b.style.borderBottomColor='transparent';b.style.color='#6b7280';});
      if(id==='pulse') window.loadPulseTab();
      if(id==='iv') window.loadIvTab(composites);
      // Restore tabs body
      const tabsBody = el.querySelector('#cahps-tabs-body');
      if(tabsBody) tabsBody.style.display='';
      const pane = el.querySelector('#ctab-pane-'+id);
      if(pane) pane.classList.add('active');
      if(btn){btn.style.borderBottomColor='#c0392b';btn.style.color='#c0392b';}"""

NEW_CAHPS_TAB_BODY = """      // Hide drilldown, restore tabs
      const drilldown = el.querySelector('#cahps-drilldown');
      if(drilldown) drilldown.remove();
      const tabsBody = el.querySelector('#cahps-tabs-body');
      if(tabsBody) tabsBody.style.display='';
      // Switch panes
      el.querySelectorAll('.cahps-tab-pane').forEach(p=>{p.classList.remove('active');p.style.opacity='0';});
      el.querySelectorAll('button[id^="ctab-"]').forEach(b=>{b.style.borderBottomColor='transparent';b.style.color='#6b7280';});
      const pane = el.querySelector('#ctab-pane-'+id);
      if(pane){
        pane.classList.add('active');
        requestAnimationFrame(()=>{pane.style.transition='opacity .18s';pane.style.opacity='1';});
      }
      if(btn){btn.style.borderBottomColor='#c0392b';btn.style.color='#c0392b';}
      // Load dynamic tabs (cached after first load)
      if(id==='pulse') window.loadPulseTab();
      if(id==='iv') window.loadIvTab(composites);"""

html = html.replace(OLD_CAHPS_TAB_BODY, NEW_CAHPS_TAB_BODY, 1)

# ── 5. Also reset cache when a new plan is selected ───────────────────────
OLD_RESET = """  window._pulseData = null;
    window._pulseContractId = contractId;"""
NEW_RESET = """  window._pulseData = null;
    window._pulseLoaded = false;
    window._ivLoaded = false;
    window._pulseContractId = contractId;"""
html = html.replace(OLD_RESET, NEW_RESET, 1)

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
checks = [
    ("composite_code:'HPR'", False, "HPR removed"),
    ("_pulseLoaded", True,  "pulse cache flag"),
    ("_ivLoaded",   True,  "iv cache flag"),
    ("opacity",     True,  "smooth fade transition"),
    ("requestAnimationFrame", True, "smooth tab switch"),
    ("drilldown.remove()", True, "drilldown cleanup"),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for needle, should_exist, label in checks:
    found = needle in content
    ok = found == should_exist
    print(f"{'OK' if ok else 'FAIL':8s} {label} ({'present' if found else 'absent'})")

# Count remaining IV composites
codes = set(re.findall(r"composite_code:'(\w+)'", content))
print(f"\nIV composites: {sorted(codes)}")
print("Done")
