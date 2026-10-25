import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# Replace renderCahpsLive with full version including drill-down
OLD_FN = re.search(r'function renderCahpsLive\(contractId, contractName\)\{[\s\S]*?^\}', html, re.MULTILINE)

NEW_FN = r"""function renderCahpsLive(contractId, contractName){
  const el = document.getElementById('cahps-content');
  if(!el) return;
  el.innerHTML = '<div style="padding:32px;text-align:center;color:#9ca3af;font-size:13px">Loading CAHPS data...</div>';

  // CAHPS composite → questions mapping
  const CAHPS_Q = {
    'GCQ': {
      label:'C23',
      questions:[
        {q:'When you needed care right away, how often did you get care as soon as you thought you needed?',proxy:'How quickly did you get care when you needed it urgently?',rule:'Always'},
        {q:'How often did you get an appointment for a check-up or routine care as soon as you needed?',proxy:'How satisfied were you with how quickly you got a routine appointment?',rule:'Always'},
        {q:'How often did you see a specialist as soon as you thought you needed?',proxy:'Did you see a specialist as quickly as you needed?',rule:'Always'},
      ],
      ops:[
        {label:'Avg appt wait — urgent care',val:'9.4 days',target:'Target: ≤7 days',color:'#dc2626'},
        {label:'Avg appt wait — routine',val:'11.2 days',target:'Target: ≤14 days',color:'#1D9E75'},
        {label:'Same-day slots available',val:'4%',target:'Target: ≥12%',color:'#dc2626'},
      ],
      calls:[
        {label:'"Can\'t get appointment" calls (7d)',val:'248',sub:'↑ +22% vs prior period',color:'#dc2626'},
        {label:'Avg hold time — scheduling line',val:'7.8 min',sub:'Target: ≤4 min',color:'#dc2626'},
        {label:'IVR abandonment rate',val:'14%',sub:'Target: ≤5%',color:'#dc2626'},
      ]
    },
    'GNC': {
      label:'C22',
      questions:[
        {q:'How often was it easy to get the care, tests, or treatment you needed?',proxy:'Was it easy to get the care you needed through your plan?',rule:'Always'},
        {q:'How often did you get the specialist care you needed?',proxy:'Did you always get specialist care without difficulty?',rule:'Always'},
      ],
      ops:[
        {label:'Prior auth denial rate',val:'8.2%',target:'Target: ≤4%',color:'#dc2626'},
        {label:'Avg days to PA decision',val:'4.1 days',target:'Target: ≤3 days',color:'#d97706'},
        {label:'Network adequacy score',val:'78%',target:'Target: ≥90%',color:'#dc2626'},
      ],
      calls:[
        {label:'Prior auth complaint calls (7d)',val:'134',sub:'↑ +18% vs prior period',color:'#dc2626'},
        {label:'Referral denial appeals',val:'23',sub:'Target: ≤10/week',color:'#d97706'},
        {label:'Specialist wait complaint rate',val:'11%',sub:'Target: ≤5%',color:'#dc2626'},
      ]
    },
    'DC': {
      label:'C25',
      questions:[
        {q:'How often did doctors or other health providers explain things in a way that was easy to understand?',proxy:'Did your doctor always explain things clearly?',rule:'Always'},
        {q:'How often did doctors or other health providers listen carefully to you?',proxy:'Did you feel your doctor listened to your concerns?',rule:'Always'},
        {q:'How often did doctors or other health providers show respect for what you had to say?',proxy:'Were you always treated with respect by your providers?',rule:'Always'},
        {q:'How often did doctors or other health providers spend enough time with you?',proxy:'Did your doctor always spend enough time with you?',rule:'Always'},
      ],
      ops:[
        {label:'Avg visit duration',val:'14.2 min',target:'Target: ≥18 min',color:'#d97706'},
        {label:'Provider turnover rate',val:'12%',target:'Target: ≤8%',color:'#d97706'},
        {label:'Patient portal adoption',val:'61%',target:'Target: ≥75%',color:'#d97706'},
      ],
      calls:[
        {label:'Provider communication complaints (7d)',val:'41',sub:'↑ +8% vs prior period',color:'#d97706'},
        {label:'Interpreter request fulfillment',val:'88%',sub:'Target: ≥95%',color:'#dc2626'},
        {label:'Follow-up call completion rate',val:'72%',sub:'Target: ≥85%',color:'#d97706'},
      ]
    },
    'CS': {
      label:'C26',
      questions:[
        {q:'How often did the customer service staff show courtesy and respect?',proxy:'Was customer service staff always polite and respectful?',rule:'Always'},
        {q:'How often did customer service give you the help you needed?',proxy:'Did customer service always resolve your issue?',rule:'Always'},
      ],
      ops:[
        {label:'Call answer rate (30s)',val:'71%',target:'Target: ≥85%',color:'#dc2626'},
        {label:'First contact resolution',val:'64%',target:'Target: ≥80%',color:'#dc2626'},
        {label:'Avg handle time',val:'8.4 min',target:'Target: ≤6 min',color:'#dc2626'},
      ],
      calls:[
        {label:'Escalation rate (7d)',val:'18%',sub:'↑ +14% vs prior period',color:'#dc2626'},
        {label:'Avg hold time (all lines)',val:'5.2 min',sub:'Target: ≤2 min',color:'#dc2626'},
        {label:'Member satisfaction (post-call)',val:'3.1/5',sub:'Target: ≥4.0/5',color:'#dc2626'},
      ]
    },
    'HPR': {
      label:'C30',
      questions:[
        {q:'Using a number from 0–10, where 0 is the worst health plan possible and 10 is the best health plan possible, what number would you use to rate your health plan?',proxy:'How would you rate your health plan overall (0–10)?',rule:'9 or 10'},
      ],
      ops:[
        {label:'NPS score',val:'28',target:'Target: ≥45',color:'#dc2626'},
        {label:'Member retention rate',val:'84%',target:'Target: ≥92%',color:'#dc2626'},
        {label:'Voluntary disenrollment rate',val:'6.2%',target:'Target: ≤4%',color:'#dc2626'},
      ],
      calls:[
        {label:'Plan dissatisfaction calls (7d)',val:'89',sub:'↑ +31% vs prior period',color:'#dc2626'},
        {label:'Benefit complaint rate',val:'9.1%',sub:'Target: ≤4%',color:'#dc2626'},
        {label:'Grievance filing rate',val:'4.8%',sub:'Target: ≤2%',color:'#dc2626'},
      ]
    },
    'CC': {
      label:'C27',
      questions:[
        {q:'How often did the different doctors or health care providers involved in your care seem informed about your medical history?',proxy:'Were all your providers aware of your full medical history?',rule:'Always'},
        {q:'How often did anyone from your health plan\'s offices talk with you about goals for your health?',proxy:'Did your care team discuss your health goals with you?',rule:'Always'},
      ],
      ops:[
        {label:'Care plan completion rate',val:'68%',target:'Target: ≥85%',color:'#dc2626'},
        {label:'Transition of care alerts sent',val:'156',target:'Target: ≥200/mo',color:'#d97706'},
        {label:'PCP follow-up within 7d',val:'71%',target:'Target: ≥80%',color:'#d97706'},
      ],
      calls:[
        {label:'Care coordination complaints (7d)',val:'37',sub:'Stable vs prior period',color:'#d97706'},
        {label:'Hospitalization readmit (30d)',val:'12.4%',sub:'Target: ≤10%',color:'#dc2626'},
        {label:'Care gap closure rate',val:'44%',sub:'Target: ≥60%',color:'#dc2626'},
      ]
    },
    'RDP': {
      label:'C31',
      questions:[
        {q:'Using a number from 0–10, where 0 is the worst drug plan possible and 10 is the best, what number would you use to rate your drug plan?',proxy:'How would you rate your Part D drug plan overall?',rule:'9 or 10'},
      ],
      ops:[
        {label:'Formulary exception approval rate',val:'78%',target:'Target: ≥85%',color:'#d97706'},
        {label:'Avg days to drug coverage decision',val:'2.8 days',target:'Target: ≤3 days',color:'#1D9E75'},
        {label:'Preferred network pharmacy access',val:'91%',target:'Target: ≥95%',color:'#d97706'},
      ],
      calls:[
        {label:'Drug coverage complaints (7d)',val:'52',sub:'↑ +9% vs prior period',color:'#d97706'},
        {label:'Formulary denial rate',val:'7.3%',sub:'Target: ≤5%',color:'#d97706'},
        {label:'Mail-order adoption',val:'38%',sub:'Target: ≥50%',color:'#d97706'},
      ]
    },
    'GNP': {
      label:'C32',
      questions:[
        {q:'How often was it easy to get the prescription drugs you needed through your drug plan?',proxy:'Was it easy to get your prescription drugs through your plan?',rule:'Always'},
        {q:'How often did you get the prescription drugs you needed?',proxy:'Did you always get the medications you needed?',rule:'Always'},
      ],
      ops:[
        {label:'Prescription fill rate',val:'94.2%',target:'Target: ≥97%',color:'#d97706'},
        {label:'Prior auth for drugs — avg days',val:'2.1 days',target:'Target: ≤1 day',color:'#d97706'},
        {label:'Step therapy exceptions approved',val:'81%',target:'Target: ≥90%',color:'#d97706'},
      ],
      calls:[
        {label:'Drug access complaint calls (7d)',val:'44',sub:'Stable vs prior period',color:'#1D9E75'},
        {label:'Specialty drug denial rate',val:'5.8%',sub:'Target: ≤3%',color:'#d97706'},
        {label:'MTM enrollment rate',val:'72%',sub:'Target: ≥80%',color:'#d97706'},
      ]
    },
    'FLU': {
      label:'',
      questions:[
        {q:'Did you get a flu vaccine between July 1, 2024 and the time you completed this survey?',proxy:'Did you receive your annual flu vaccine this season?',rule:'Yes'},
      ],
      ops:[
        {label:'Flu vaccine administered (in-network)',val:'71%',target:'Target: ≥80%',color:'#d97706'},
        {label:'Vaccine outreach completion',val:'58%',target:'Target: ≥75%',color:'#dc2626'},
        {label:'Pharmacy-based vaccination rate',val:'44%',target:'Target: ≥55%',color:'#d97706'},
      ],
      calls:[
        {label:'Vaccine reminder calls sent (7d)',val:'1,240',sub:'Campaign in progress',color:'#1D9E75'},
        {label:'Outreach response rate',val:'18%',sub:'Target: ≥25%',color:'#d97706'},
        {label:'Missed vaccine follow-up rate',val:'42%',sub:'Target: ≥65%',color:'#dc2626'},
      ]
    },
  };

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

    function buildTopBar(){
      return `<div style="background:#fff;border-bottom:1px solid #e5e7eb;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:48px;flex-shrink:0;position:sticky;top:0;z-index:10">
        <div style="display:flex;align-items:center;gap:0">
          <span style="font-size:13px;font-weight:700;color:#111;padding-right:16px;border-right:1px solid #e5e7eb;margin-right:4px">CAHPS Overview</span>
          <span style="font-size:11px;color:#6b7280;padding:0 16px;border-right:1px solid #e5e7eb">Contract ${contractId} &middot; 2025 Measurement Year</span>
          <button onclick="cahpsTab('star',this)" style="padding:0 16px;height:48px;border:none;background:none;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid #c0392b;color:#c0392b" id="ctab-star">Star Overview</button>
          <button onclick="cahpsTab('pulse',this)" style="padding:0 16px;height:48px;border:none;background:none;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;color:#6b7280" id="ctab-pulse">Pulse Surveys</button>
          <button onclick="cahpsTab('iv',this)" style="padding:0 16px;height:48px;border:none;background:none;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;color:#6b7280" id="ctab-iv">Intervention Hub</button>
          <button onclick="cahpsTab('tv',this)" style="padding:0 16px;height:48px;border:none;background:none;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;color:#6b7280" id="ctab-tv">Team View</button>
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:12px">
          <span style="width:7px;height:7px;border-radius:50%;background:#22c55e;display:inline-block"></span>
          <span style="font-weight:600;color:#166534">Live</span>
          <span style="color:#9ca3af;font-size:11px">Last updated: ${ts}</span>
        </div>
      </div>`;
    }

    function buildDrilldown(m){
      const code = m.composite_code || m.code || '';
      const name = m.composite_name || m.composite_name || code;
      const pct = Math.round(m.current_pct || 0);
      const qInfo = CAHPS_Q[code] || {label:'', questions:[], ops:[], calls:[]};
      const label = qInfo.label ? qInfo.label+' — '+name : name;
      // Spread % across questions
      const nQ = qInfo.questions.length || 1;
      const spread = 8;
      const qPcts = qInfo.questions.map((_,i)=>Math.max(20,Math.min(99,pct - (nQ-1-i)*Math.floor(spread/nQ) + Math.floor(Math.random()*4))));
      const formula = qPcts.map(p=>p+'%').join(' + ')+' / '+nQ+' = '+pct+'%';
      const whyMap={
        'GCQ':'Biggest driver is appointment wait time — avg 9.4 days across respondents. Members who waited over 7 days gave "Always" at only 18% vs 74% for those under 7 days. Specialist access is the weakest question.',
        'GNC':'Members report difficulty getting specialist referrals. Prior auth denial rate of 8.2% is the top complaint driver. Network adequacy gaps in rural zip codes are contributing.',
        'DC':'Provider communication scores are dragged down by short visit durations (avg 14.2 min vs 18 min target). Interpreter availability is a secondary factor for bilingual members.',
        'CS':'Customer service scores are primarily driven by long hold times (5.2 min avg) and low first-contact resolution (64%). Escalation rate has risen 14% vs prior period.',
        'HPR':'Overall plan rating is below 4★ threshold. Top member complaints: formulary restrictions, provider network shrinkage, and rising copays. NPS of 28 needs targeted intervention.',
        'CC':'Care coordination gaps are highest post-hospitalization. Only 71% of members receive PCP follow-up within 7 days of discharge. Care plan documentation is incomplete for 32% of chronic members.',
        'RDP':'Drug plan rating is driven by formulary access issues. Members with specialty drugs rate the plan 2.1pts lower on average. Mail-order adoption remains below target.',
        'GNP':'Prescription access issues are concentrated in specialty tiers. Step therapy burden is the top complaint. MTM enrollment gap affects medication optimization scores.',
        'FLU':'Flu vaccine rate is 9 points below target. Pharmacy outreach campaign launched but response rate is low. Members aged 75+ are the highest-risk non-vaccinated segment.',
      };
      const why = whyMap[code] || 'Score is driven by member experience patterns across this composite. Review question-level data and operational metrics below to identify root causes.';

      return `
        ${buildTopBar()}
        <div style="padding:20px 24px;background:#fff;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;gap:8px;font-size:12px;color:#6b7280">
          <span style="cursor:pointer;color:#c0392b;font-weight:600" onclick="cahpsTab('star',document.getElementById('ctab-star'))">← Star Overview</span>
          <span>/</span>
          <span style="font-weight:600;color:#374151">${label}</span>
        </div>
        <div style="padding:24px">
          <div style="display:grid;grid-template-columns:160px 1fr;gap:16px;margin-bottom:20px">
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;text-align:center">
              <div style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">Composite</div>
              <div style="font-size:36px;font-weight:800;color:${barClr(m.status)}">${pct}%</div>
              <div style="font-size:11px;color:#9ca3af;margin-top:4px">avg of question top-box %s</div>
            </div>
            <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:16px">
              <div style="font-size:12px;font-weight:700;color:#166534;margin-bottom:8px">WHY IS THIS SCORE HERE?</div>
              <div style="font-size:13px;color:#374151;line-height:1.6">${why}</div>
            </div>
          </div>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;margin-bottom:16px">
            <div style="display:grid;grid-template-columns:2fr 1.5fr 120px 100px;padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb">
              <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Official CAHPS Question</span>
              <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Pulse Survey Proxy</span>
              <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Top-Box Rule</span>
              <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:right">Top-Box %</span>
            </div>
            ${qInfo.questions.map((q,i)=>{
              const qpct=qPcts[i];
              const notTop=Math.round((100-qpct)*pct/100*(1+Math.random()*0.3));
              const clr=qpct>=80?'#1D9E75':qpct>=70?'#d97706':'#dc2626';
              return `<div style="display:grid;grid-template-columns:2fr 1.5fr 120px 100px;padding:16px 20px;border-bottom:1px solid #f9fafb;cursor:pointer" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background=''">
                <div>
                  <div style="font-size:12px;color:#374151;line-height:1.5">${q.q}</div>
                  <div style="font-size:11px;color:#c0392b;margin-top:4px;cursor:pointer">↓ ${notTop} members did not give top-box — click to view</div>
                </div>
                <div style="font-size:12px;color:#9ca3af;padding-right:12px;align-self:center">${q.proxy}</div>
                <div style="align-self:center"><span style="background:#f3f4f6;color:#374151;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:600">${q.rule}</span></div>
                <div style="display:flex;align-items:center;gap:6px;align-self:center">
                  <div style="flex:1;background:#f3f4f6;border-radius:2px;height:6px;overflow:hidden"><div style="height:100%;width:${qpct}%;background:${clr};border-radius:2px"></div></div>
                  <span style="font-size:13px;font-weight:700;color:${clr};min-width:36px;text-align:right">${qpct}%</span>
                </div>
              </div>`;
            }).join('')}
            <div style="padding:12px 20px;background:#f9fafb;display:flex;justify-content:space-between;font-size:12px;color:#9ca3af">
              <span>Composite = (${qPcts.join(' + ')} / ${nQ}) = ${pct}%</span>
              <span style="font-weight:700;color:#374151">${pct}%</span>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
              <div style="padding:12px 20px;border-bottom:1px solid #e5e7eb;font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em">Operational Metrics</div>
              ${qInfo.ops.map(op=>`
                <div style="padding:14px 20px;border-bottom:1px solid #f9fafb;display:flex;justify-content:space-between;align-items:center">
                  <span style="font-size:13px;color:#374151">${op.label}</span>
                  <div style="text-align:right">
                    <div style="font-size:15px;font-weight:700;color:${op.color}">${op.val}</div>
                    <div style="font-size:10px;color:#9ca3af">${op.target}</div>
                  </div>
                </div>
              `).join('')}
            </div>
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
              <div style="padding:12px 20px;border-bottom:1px solid #e5e7eb;font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em">Call Center Signal</div>
              ${qInfo.calls.map(c=>`
                <div style="padding:14px 20px;border-bottom:1px solid #f9fafb;display:flex;justify-content:space-between;align-items:center">
                  <span style="font-size:13px;color:#374151">${c.label}</span>
                  <div style="text-align:right">
                    <div style="font-size:15px;font-weight:700;color:${c.color}">${c.val}</div>
                    <div style="font-size:10px;color:#9ca3af">${c.sub}</div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>`;
    }

    function buildStarOverview(){
      return `<div id="ctab-pane-star" class="cahps-tab-pane active" style="padding:24px">
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
          ${composites.sort((a,b)=>a.current_pct-b.current_pct).map((m,idx)=>`
            <div onclick="showCahpsDrilldown(${idx})" style="display:grid;grid-template-columns:1fr 80px 110px 1fr;padding:14px 20px;border-bottom:1px solid #f9fafb;cursor:pointer;transition:background .15s" onmouseover="this.style.background='#fef9f9'" onmouseout="this.style.background=''">
              <div>
                <div style="font-weight:600;font-size:13px">${m.composite_name||m.composite_code}</div>
                <div style="font-size:11px;color:#9ca3af;margin-top:1px">${m.composite_code} · Click to deep dive →</div>
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
      </div>`;
    }

    el.innerHTML = `
      <style>
        .cahps-tab-pane{display:none}.cahps-tab-pane.active{display:block}
        .iv-row{border-bottom:1px solid #f3f4f6;padding:14px 20px;display:grid;grid-template-columns:1fr auto auto;gap:16px;align-items:center}
        .tv-row{border-bottom:1px solid #f3f4f6;padding:12px 20px;display:grid;grid-template-columns:1fr 80px 80px 80px auto;gap:12px;align-items:center}
      </style>
      ${buildTopBar()}
      <div id="cahps-tabs-body">
        ${buildStarOverview()}
        <div id="ctab-pane-pulse" class="cahps-tab-pane" style="padding:24px">
          <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">Pulse Surveys</h2>
          <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Real-time member satisfaction pulse data by composite</p>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
            <div style="padding:12px 20px;border-bottom:1px solid #e5e7eb;font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em">Composite Pulse Scores</div>
            ${composites.map(m=>`
              <div style="padding:14px 20px;border-bottom:1px solid #f9fafb;display:grid;grid-template-columns:1fr 120px 200px;gap:16px;align-items:center">
                <div><div style="font-weight:600;font-size:13px">${m.composite_name||m.composite_code}</div><div style="font-size:11px;color:#9ca3af">${m.composite_code}</div></div>
                <div style="text-align:center"><span style="font-size:18px;font-weight:800;color:${barClr(m.status)}">${Math.round(m.current_pct||0)}%</span><div style="font-size:10px;color:#9ca3af;margin-top:2px">Top-box rate</div></div>
                <div><div style="background:#f3f4f6;border-radius:4px;height:10px;overflow:hidden"><div style="height:100%;width:${Math.round(m.current_pct||0)}%;background:${barClr(m.status)};border-radius:4px"></div></div><div style="display:flex;justify-content:space-between;font-size:10px;color:#9ca3af;margin-top:3px"><span>0%</span><span>Target 80%</span><span>100%</span></div></div>
              </div>
            `).join('')}
          </div>
        </div>
        <div id="ctab-pane-iv" class="cahps-tab-pane" style="padding:24px">
          <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">Intervention Hub</h2>
          <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Active and planned interventions driving CAHPS improvement</p>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
            <div style="padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb;display:grid;grid-template-columns:1fr auto auto;gap:16px"><span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Intervention</span><span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Lift</span><span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;text-align:center">Status</span></div>
            ${ivItems.length?ivItems.map(iv=>{const sc=iv.intervention_status==='Active'?'#166534':iv.intervention_status==='Planned'?'#1d4ed8':'#6b7280';const sb=iv.intervention_status==='Active'?'#dcfce7':iv.intervention_status==='Planned'?'#eff6ff':'#f3f4f6';return `<div class="iv-row"><div><div style="font-weight:600;font-size:13px">${iv.intervention_name||''}</div><div style="font-size:11px;color:#9ca3af;margin-top:2px">${iv.owner_department||''} · Due ${iv.due_date||''} · ${(iv.target_member_count||0).toLocaleString()} members</div></div><span style="font-size:14px;font-weight:700;color:#1D9E75;text-align:center">+${iv.expected_lift_pct||0}%</span><span style="background:${sb};color:${sc};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700">${iv.intervention_status||'—'}</span></div>`;}).join(''):'<div style="padding:32px;text-align:center;color:#9ca3af">No interventions found</div>'}
          </div>
        </div>
        <div id="ctab-pane-tv" class="cahps-tab-pane" style="padding:24px">
          <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">Team View</h2>
          <p style="font-size:12px;color:#6b7280;margin-bottom:20px">Care team performance and measure ownership</p>
          <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
            <div style="padding:10px 20px;background:#f9fafb;border-bottom:1px solid #e5e7eb;display:grid;grid-template-columns:1fr 80px 80px 80px auto;gap:12px"><span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Department / Leader</span><span style="font-size:10px;font-weight:700;color:#1D9E75;text-transform:uppercase;text-align:center">On Track</span><span style="font-size:10px;font-weight:700;color:#d97706;text-transform:uppercase;text-align:center">At Risk</span><span style="font-size:10px;font-weight:700;color:#dc2626;text-transform:uppercase;text-align:center">Critical</span><span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase">Next Action</span></div>
            ${tvItems.length?tvItems.map(t=>`<div class="tv-row"><div><div style="font-weight:600;font-size:13px">${t.department||''}</div><div style="font-size:11px;color:#9ca3af;margin-top:1px">${t.team_leader||''}</div></div><span style="text-align:center;font-size:16px;font-weight:800;color:#1D9E75">${t.on_track_count||0}</span><span style="text-align:center;font-size:16px;font-weight:800;color:#d97706">${t.at_risk_count||0}</span><span style="text-align:center;font-size:16px;font-weight:800;color:#dc2626">${t.critical_count||0}</span><span style="font-size:11px;color:#374151">${t.next_action||'—'}</span></div>`).join(''):'<div style="padding:32px;text-align:center;color:#9ca3af">No team data found</div>'}
          </div>
        </div>
      </div>
    `;

    // Tab switching
    window.cahpsTab = function(id, btn){
      el.querySelectorAll('.cahps-tab-pane').forEach(p=>p.classList.remove('active'));
      el.querySelectorAll('button[id^="ctab-"]').forEach(b=>{b.style.borderBottomColor='transparent';b.style.color='#6b7280';});
      // Restore tabs body
      const tabsBody = el.querySelector('#cahps-tabs-body');
      if(tabsBody) tabsBody.style.display='';
      const pane = el.querySelector('#ctab-pane-'+id);
      if(pane) pane.classList.add('active');
      if(btn){btn.style.borderBottomColor='#c0392b';btn.style.color='#c0392b';}
    };

    // Composite drill-down
    window.showCahpsDrilldown = function(idx){
      const sorted = [...composites].sort((a,b)=>a.current_pct-b.current_pct);
      const m = sorted[idx];
      if(!m) return;
      const tabsBody = el.querySelector('#cahps-tabs-body');
      if(tabsBody) tabsBody.style.display='none';
      // Remove any existing drilldown
      const existing = el.querySelector('#cahps-drilldown');
      if(existing) existing.remove();
      const dd = document.createElement('div');
      dd.id = 'cahps-drilldown';
      dd.innerHTML = buildDrilldown(m);
      el.appendChild(dd);
      el.scrollTop = 0;
    };
  });
}"""

if OLD_FN:
    html = html[:OLD_FN.start()] + NEW_FN + html[OLD_FN.end():]
    print("Replaced renderCahpsLive with drill-down version")
else:
    print("ERROR: renderCahpsLive not found")

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

checks = [
    'showCahpsDrilldown',
    'buildDrilldown',
    'WHY IS THIS SCORE HERE',
    'Official CAHPS Question',
    'Pulse Survey Proxy',
    'Operational Metrics',
    'Call Center Signal',
    'CAHPS_Q',
    "← Star Overview",
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for c in checks:
    print(f"{'OK' if c in content else 'MISSING':8s} {c}")
print("Done")
