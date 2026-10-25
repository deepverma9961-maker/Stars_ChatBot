import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# Replace the Intervention Hub pane
OLD_IV = re.search(
    r'<div id="ctab-pane-iv" class="cahps-tab-pane"[\s\S]*?</div>\s*<div id="ctab-pane-tv"',
    html
)

NEW_IV = '''<div id="ctab-pane-iv" class="cahps-tab-pane" style="padding:24px">
          <div id="iv-loading" style="text-align:center;color:#9ca3af;padding:32px">Loading interventions...</div>
          <div id="iv-body" style="display:none"></div>
          <!-- Leadership Report Modal -->
          <div id="iv-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:9999;overflow-y:auto;padding:40px 0" onclick="if(event.target===this)closeIvModal()">
            <div style="background:#fff;max-width:680px;margin:0 auto;border-radius:12px;overflow:hidden;position:relative" onclick="event.stopPropagation()">
              <div id="iv-modal-content"></div>
            </div>
          </div>
        </div>
        <div id="ctab-pane-tv"'''

if OLD_IV:
    html = html[:OLD_IV.start()] + NEW_IV + html[OLD_IV.end()-len('<div id="ctab-pane-tv"'):]
    print("Replaced Intervention Hub pane")
else:
    print("ERROR: iv pane not found")

# Add loadIvTab function and modal helpers before cahpsTab function
IV_LOADER = r"""window.closeIvModal = function(){
      document.getElementById('iv-modal').style.display='none';
    };
    window.openIvModal = function(iv, composites){
      const modal = document.getElementById('iv-modal');
      const score = composites.find(c=>c.composite_code===iv.composite_code);
      const pct = score ? Math.round(score.current_pct||0) : 0;
      const sendEmail = 'mailto:' + iv.send_email + '?subject=Leadership Report: ' + encodeURIComponent(iv.name) + '&body=' + encodeURIComponent(
        'Leadership Report — CAHPS Performance\n\n'+iv.name+'\nComposite: '+iv.composite_label+' — '+iv.composite_name+'\nOwner: '+iv.owner+'\nStatus: '+iv.status+'\n\nHeadline Finding:\n'+iv.headline+'\n\nRequired Action:\n'+iv.action+'\n\nDefinition of Done:\n'+iv.done
      );
      document.getElementById('iv-modal-content').innerHTML = `
        <div style="background:#1a1a2e;padding:24px 28px;color:#fff">
          <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px">Leadership Report — CAHPS Performance</div>
          <div style="font-size:20px;font-weight:800;line-height:1.3;margin-bottom:8px">${iv.name}</div>
          <div style="font-size:12px;color:#9ca3af">To: ${iv.to} &middot; VP of Provider Relations &middot; Stars Program Director</div>
          <button onclick="closeIvModal()" style="position:absolute;top:16px;right:16px;width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.15);border:none;color:#fff;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center">×</button>
        </div>
        <div style="padding:24px 28px">
          <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">
            <span style="background:#fef2f2;color:#c0392b;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #fecaca">${iv.composite_label} — ${iv.composite_name}</span>
            <span style="background:#f3f4f6;color:#374151;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600">Owner: ${iv.owner}</span>
            <span style="background:${iv.status==='In Progress'?'#fffbeb':'#fef2f2'};color:${iv.status==='In Progress'?'#92400e':'#c0392b'};padding:5px 12px;border-radius:20px;font-size:12px;font-weight:700">${iv.status}</span>
          </div>
          <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:16px;margin-bottom:20px">
            <div style="font-size:10px;font-weight:700;color:#92400e;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Headline Finding</div>
            <div style="font-size:14px;color:#374151;line-height:1.6">${iv.headline}</div>
          </div>
          <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px">What is Going Wrong — Specific Metrics</div>
          <div style="margin-bottom:20px">
            ${iv.wrong_metrics.map(m=>`<div style="display:flex;gap:10px;padding:10px 0;border-bottom:1px solid #f3f4f6;align-items:flex-start"><span style="color:#c0392b;font-size:16px;line-height:1;flex-shrink:0">●</span><span style="font-size:13px;color:#374151;line-height:1.5">${m}</span></div>`).join('')}
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px">
            <div style="background:#f9fafb;border-radius:8px;padding:16px">
              <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">Current</div>
              <div style="font-size:28px;font-weight:800;color:#c0392b">${iv.current_val}</div>
              <div style="font-size:12px;color:#6b7280;margin-top:3px">${iv.metric}</div>
            </div>
            <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:16px">
              <div style="font-size:10px;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">Target Needed for 4★</div>
              <div style="font-size:28px;font-weight:800;color:#1D9E75">${iv.target_val}</div>
              <div style="font-size:12px;color:#166534;margin-top:3px">${iv.metric}</div>
            </div>
          </div>
          <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">Required Action</div>
          <div style="background:#f9fafb;border-radius:8px;padding:14px;font-size:13px;color:#374151;line-height:1.6;margin-bottom:16px">${iv.action}</div>
          <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:14px;margin-bottom:24px">
            <div style="font-size:10px;font-weight:700;color:#1d4ed8;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Definition of Done</div>
            <div style="font-size:13px;color:#1d4ed8">${iv.done}</div>
          </div>
          <div style="display:flex;justify-content:center;gap:12px">
            <button onclick="closeIvModal()" style="padding:10px 28px;border:1px solid #e5e7eb;border-radius:8px;background:#fff;font-size:13px;font-weight:600;cursor:pointer;color:#374151">Close</button>
            <a href="${sendEmail}" style="padding:10px 24px;background:#1a1a2e;color:#fff;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:6px">↑ Send to ${iv.send_to}</a>
          </div>
        </div>
      `;
      modal.style.display='block';
    };
    window.loadIvTab = function(composites){
      const body = document.getElementById('iv-body');
      const loading = document.getElementById('iv-loading');
      if(!body) return;
      if(loading) loading.style.display='none';
      body.style.display='';

      // CAHPS process improvements per composite — uses live composite score for current CAHPS %
      const getScore = code => { const c=composites.find(x=>x.composite_code===code); return c?Math.round(c.current_pct||0):0; };
      const IV_DATA = [
        {composite_code:'GCQ',composite_label:'C23',composite_name:'Getting Care Quickly',
         name:'Implement same-day slot release using no-show prediction model',owner:'Network Ops',
         to:'Director of Network Operations',send_to:'Director of Network Operations',send_email:'network.ops@healthplan.com',
         metric:'Same-day slot availability',current_val:'4%',target_val:'≥12%',status:'Not Started',
         headline:'Same-day appointment slot availability is critically low at 4% vs the 12% target needed for C23 top-box performance.',
         wrong_metrics:['Same-day slot availability: 4% (target ≥12%) — gap of 8 percentage points','Average urgent care wait: 9.4 days (target ≤7 days)','No-show rate across PCPs: 18% — these slots are going unfilled rather than being released','94 members gave Sometimes/Never on urgent care access in the last pulse survey','Specialist referral TAT: 8.1 days (target ≤5 days)'],
         action:'Deploy no-show prediction model to release same-day slots automatically. Requires scheduling system integration with Epic. Engage top 20 PCPs by member volume first.',
         done:'Same-day availability ≥12% sustained for 4 consecutive weeks'},
        {composite_code:'GCQ',composite_label:'C23',composite_name:'Getting Care Quickly',
         name:'Reduce specialist referral turnaround time via automated routing',owner:'Provider Relations',
         to:'Director of Provider Relations',send_to:'Director of Provider Relations',send_email:'provider.relations@healthplan.com',
         metric:'Specialist referral TAT',current_val:'8.1 days',target_val:'≤5 days',status:'Not Started',
         headline:'Specialist referral turnaround is 62% over target at 8.1 days. Manual routing adds 3-4 days of unnecessary delay.',
         wrong_metrics:['Specialist referral TAT: 8.1 days (target ≤5 days)','Manual routing used in 73% of referrals','72% of delayed referrals are to 5 high-demand specialty groups','169 members cited specialist access as reason for "Sometimes/Never" response'],
         action:'Implement auto-routing for top 5 specialty types using network capacity data. Pilot with cardiology and orthopedics first.',
         done:'Specialist referral TAT ≤5 days for ≥80% of referrals for 8 consecutive weeks'},
        {composite_code:'GCQ',composite_label:'C23',composite_name:'Getting Care Quickly',
         name:'Enable online self-scheduling across all in-network PCPs',owner:'Digital / IT',
         to:'Chief Information Officer',send_to:'Chief Information Officer',send_email:'cio@healthplan.com',
         metric:'Online self-scheduling rate',current_val:'22%',target_val:'≥40%',status:'Not Started',
         headline:'Only 22% of member scheduling interactions use the digital self-scheduling portal. Low adoption forces members to call, increasing wait times.',
         wrong_metrics:['Online self-scheduling rate: 22% (target ≥40%)','78% of PCP appointments still booked via phone','Average phone booking wait: 8.4 minutes','Member satisfaction for phone booking: 3.1/5 vs 4.2/5 for online'],
         action:'Mandate digital scheduling API integration for all contracted PCPs by Q3 2025. Provide member onboarding incentive ($10 credit) for portal registration.',
         done:'Online self-scheduling rate ≥40% sustained across contracted PCP network'},
        {composite_code:'CS',composite_label:'C24',composite_name:'Customer Service',
         name:'Implement mandatory FCR callback protocol for all unresolved calls',owner:'Call Center Ops',
         to:'Call Center Operations Manager',send_to:'Call Center Operations Manager',send_email:'callcenter.ops@healthplan.com',
         metric:'First-call resolution rate',current_val:'71%',target_val:'≥82%',status:'In Progress',
         headline:'First-call resolution at 71% is 11 points below the 82% target. Unresolved calls are the top driver of low Customer Service scores.',
         wrong_metrics:['FCR rate: 71% (target ≥82%) — 278 calls per week require callback','Avg callback completion rate: 58% — 42% of members never reached','Call abandonment rate: 14% (target ≤5%)','Member satisfaction post-unresolved call: 2.4/5'],
         action:'Deploy mandatory callback tracking system. All unresolved calls must be closed within 24h or escalated. Agent accountability dashboard to be reviewed weekly.',
         done:'FCR ≥82% sustained for 6 consecutive weeks with callback closure rate ≥90%'},
        {composite_code:'CS',composite_label:'C24',composite_name:'Customer Service',
         name:'Deploy real-time agent assist copilot for resolution guidance during calls',owner:'Call Center / IT',
         to:'Call Center Operations Manager',send_to:'Call Center Operations Manager',send_email:'callcenter.ops@healthplan.com',
         metric:'Negative sentiment call rate',current_val:'18%',target_val:'≤8%',status:'Not Started',
         headline:'18% of calls exhibit negative sentiment patterns. Real-time AI guidance could resolve most cases before escalation.',
         wrong_metrics:['Negative sentiment call rate: 18% (target ≤8%)','Top negative-sentiment triggers: billing disputes (34%), prior auth denials (28%), specialist access (22%)','Escalation rate: 18% — 3× the target rate'],
         action:'Deploy NLP-based agent assist overlay that surfaces resolution scripts during live calls. Integrate with CRM for real-time member context.',
         done:'Negative sentiment call rate ≤8% for 8 consecutive weeks'},
        {composite_code:'CS',composite_label:'C24',composite_name:'Customer Service',
         name:'Redesign IVR routing to ≤2 menu levels and expand after-hours coverage',owner:'Call Center Ops',
         to:'Call Center Operations Manager',send_to:'Call Center Operations Manager',send_email:'callcenter.ops@healthplan.com',
         metric:'IVR abandonment rate',current_val:'9%',target_val:'≤5%',status:'Not Started',
         headline:'IVR abandonment at 9% is nearly double the target. Complex menu trees cause members to hang up before reaching an agent.',
         wrong_metrics:['IVR abandonment rate: 9% (target ≤5%)','Current IVR has 4 menu levels — best practice is ≤2','After-hours coverage ends at 8pm; 23% of calls come between 8pm–11pm'],
         action:'Redesign IVR tree to ≤2 menu levels. Expand after-hours chat coverage to 11pm. Implement virtual hold with callback option.',
         done:'IVR abandonment ≤5% and after-hours coverage extended to 11pm'},
        {composite_code:'GNC',composite_label:'C22',composite_name:'Getting Needed Care',
         name:'Implement AI pre-screening to auto-approve standard prior auth cases',owner:'UM / IT',
         to:'Utilization Management Director',send_to:'Utilization Management Director',send_email:'um.director@healthplan.com',
         metric:'Prior auth denial rate',current_val:'18%',target_val:'≤8%',status:'Not Started',
         headline:'Prior authorization denial rate of 18% is the top complaint driver for Getting Needed Care. Standard cases are taking 4+ days due to manual review.',
         wrong_metrics:['Prior auth denial rate: 18% (target ≤8%)','73% of denials are for standard/routine procedures that could be auto-approved','Average PA decision time: 4.1 days (target ≤1 day)','134 prior auth complaint calls in the past 7 days'],
         action:'Deploy ML model to auto-approve standard PA cases (estimated 73% of volume). Requires UM policy update and state regulatory review.',
         done:'Prior auth denial rate ≤8% with auto-approval for standard cases within 4h'},
        {composite_code:'GNC',composite_label:'C22',composite_name:'Getting Needed Care',
         name:'Build formulary alternative notification at point of pharmacy denial',owner:'Pharmacy / IT',
         to:'Pharmacy Director',send_to:'Pharmacy Director',send_email:'pharmacy.director@healthplan.com',
         metric:'Formulary exception approval rate',current_val:'61%',target_val:'≥80%',status:'Not Started',
         headline:'Formulary exception approval rate of 61% is 19 points below target. Members denied formulary drugs have no automated pathway to alternatives.',
         wrong_metrics:['Formulary exception approval rate: 61% (target ≥80%)','Average days to formulary decision: 2.8 days','Specialty drug denial rate: 5.8% (target ≤3%)'],
         action:'Build real-time formulary alternative notification at point of pharmacy denial. Pharmacists receive push notification with covered alternatives within 1 hour.',
         done:'Formulary exception approval rate ≥80% with alternative notification within 1h for 90% of denials'},
        {composite_code:'CC',composite_label:'C27',composite_name:'Care Coordination',
         name:'EHR integration: automated test result notification to patient within 24h',owner:'Clinical / IT',
         to:'Chief Medical Officer',send_to:'Chief Medical Officer',send_email:'cmo@healthplan.com',
         metric:'Test result notification rate',current_val:'81%',target_val:'≥90%',status:'In Progress',
         headline:'19% of test results are not communicated to patients within 24 hours. This is the leading driver of low Care Coordination scores.',
         wrong_metrics:['Test result notification rate: 81% (target ≥90%)','Average notification delay: 3.2 days for non-critical results','32% of chronic care members have incomplete care plan documentation'],
         action:'Integrate EHR notification engine with patient portal. All test results auto-pushed within 24h. Critical results trigger immediate provider alert.',
         done:'Test result notification rate ≥90% within 24h sustained for 8 consecutive weeks'},
        {composite_code:'HPR',composite_label:'Overall Plan Rating',composite_name:'Overall Plan Rating',
         name:'Implement structured service recovery programme triggered by negative NLP sentiment',owner:'Member Experience',
         to:'Member Experience Director',send_to:'Member Experience Director',send_email:'memberexp.director@healthplan.com',
         metric:'Service recovery contact rate',current_val:'46%',target_val:'≥90%',status:'In Progress',
         headline:'Only 46% of members who express negative sentiment receive a structured service recovery outreach. This is the primary driver of low overall plan ratings.',
         wrong_metrics:['Service recovery contact rate: 46% (target ≥90%)','NPS: 28 (target ≥45)','Member retention rate: 84% (target ≥92%)','Voluntary disenrollment rate: 6.2% (target ≤4%)'],
         action:'Deploy NLP pipeline to flag all negative-sentiment interactions (calls, surveys, portal messages). Trigger 48h service recovery outreach with dedicated concierge team.',
         done:'Service recovery contact rate ≥90% within 48h for all flagged negative-sentiment interactions'},
      ];

      // Group by composite
      const grouped = {};
      IV_DATA.forEach(iv=>{
        const key = iv.composite_code;
        if(!grouped[key]) grouped[key]={label:iv.composite_label,name:iv.composite_name,items:[]};
        grouped[key].items.push(iv);
      });

      const inProgress = IV_DATA.filter(iv=>iv.status==='In Progress').length;
      const notStarted = IV_DATA.filter(iv=>iv.status==='Not Started').length;
      const days = 47; // from CAHPS data

      const stCl = s => s==='In Progress'?'#d97706':'#c0392b';
      const stBg = s => s==='In Progress'?'#fffbeb':'#fef2f2';

      body.innerHTML = `
        <div style="background:#1a1a2e;border-radius:12px;padding:20px 24px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center">
          <div style="display:flex;gap:40px">
            <div><div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">Process Improvements</div><div style="font-size:28px;font-weight:800;color:#fff">${IV_DATA.length}</div></div>
            <div><div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">In Progress</div><div style="font-size:28px;font-weight:800;color:#d97706">${inProgress}</div></div>
            <div><div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">Not Started</div><div style="font-size:28px;font-weight:800;color:#c0392b">${notStarted}</div></div>
            <div><div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">Survey Window</div><div style="font-size:28px;font-weight:800;color:#fff">${days}d</div></div>
          </div>
          <div style="display:flex;gap:10px">
            <button style="padding:10px 18px;background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2);border-radius:8px;font-size:12px;font-weight:600;cursor:pointer">↑ Send all department reports</button>
            <button style="padding:10px 18px;background:#c0392b;color:#fff;border:none;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer">↑ Send leadership report</button>
          </div>
        </div>
        ${Object.entries(grouped).map(([code,grp])=>`
          <div style="margin-bottom:28px">
            <div style="font-size:12px;font-weight:800;color:#c0392b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px">${grp.label} — ${grp.name.toUpperCase()}</div>
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
              <div style="display:grid;grid-template-columns:2fr 1fr 1.2fr 80px 80px 100px 80px;padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb;gap:12px">
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Process Improvement</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Owner</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Metric</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:right">Current</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:right">Target</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Status</span>
                <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Report</span>
              </div>
              ${grp.items.map((iv,idx)=>`
                <div style="display:grid;grid-template-columns:2fr 1fr 1.2fr 80px 80px 100px 80px;padding:16px 20px;border-bottom:1px solid #f9fafb;gap:12px;align-items:center" onmouseover="this.style.background='#fafafa'" onmouseout="this.style.background=''">
                  <div>
                    <div style="font-size:13px;font-weight:600;line-height:1.4">${iv.name}</div>
                    <div style="font-size:11px;color:#9ca3af;margin-top:3px">To: ${iv.to}</div>
                  </div>
                  <div style="font-size:12px;color:#374151">${iv.owner}</div>
                  <div style="font-size:12px;color:#9ca3af">${iv.metric}</div>
                  <div style="font-size:13px;font-weight:700;color:#c0392b;text-align:right">${iv.current_val}</div>
                  <div style="font-size:13px;font-weight:600;color:#1D9E75;text-align:right">${iv.target_val}</div>
                  <div style="text-align:center"><span style="background:${stBg(iv.status)};color:${stCl(iv.status)};padding:4px 8px;border-radius:6px;font-size:11px;font-weight:700;white-space:nowrap">${iv.status}</span></div>
                  <div style="text-align:center"><button onclick='openIvModal(${JSON.stringify(iv).replace(/'/g,"&apos;")}, ${JSON.stringify(composites)})' style="padding:5px 12px;border:1px solid #e5e7eb;border-radius:6px;background:#fff;font-size:12px;font-weight:600;cursor:pointer;color:#374151" onmouseover="this.style.background='#fef2f2';this.style.borderColor='#fecaca';this.style.color='#c0392b'" onmouseout="this.style.background='#fff';this.style.borderColor='#e5e7eb';this.style.color='#374151'">View →</button></div>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      `;
    };
    window.cahpsTab = function(id, btn){"""

html = html.replace("    window.cahpsTab = function(id, btn){", IV_LOADER, 1)

# Trigger iv load when iv tab is clicked - find the pulse trigger and add iv trigger
OLD_ACT = "      if(id==='pulse') window.loadPulseTab();"
NEW_ACT = "      if(id==='pulse') window.loadPulseTab();\n      if(id==='iv') window.loadIvTab(composites);"
html = html.replace(OLD_ACT, NEW_ACT, 1)

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

checks = [
    'loadIvTab',
    'openIvModal',
    'closeIvModal',
    'IV_DATA',
    'Leadership Report',
    'Headline Finding',
    'What is Going Wrong',
    'Required Action',
    'Definition of Done',
    'mailto:',
    'Send to',
    'Process Improvement',
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for c in checks:
    print(f"{'OK' if c in content else 'MISSING':8s} {c}")
print("Done")
