import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# Find and replace the entire initApp function with a fast parallel version
OLD_INIT = re.search(r'async function initApp\(\)\{[\s\S]*?initApp\(\);', html)

NEW_INIT = r"""async function initApp(){
  // Fast fetch with timeout — fail quickly if API is slow
  function ft(url, ms=8000){
    const ac=new AbortController();
    const id=setTimeout(()=>ac.abort(),ms);
    return fetch(url,{signal:ac.signal}).then(r=>{clearTimeout(id);return r.json();}).catch(()=>null);
  }

  // ── Connection status badge (non-blocking, runs in background) ────────
  const badge=document.getElementById('data-source-badge');
  const dsLabel=document.getElementById('ds-label');
  const tooltip=document.getElementById('data-source-tooltip');
  ft('/api/connection-status',6000).then(cs=>{
    if(cs&&cs.connected&&cs.source==='live'){
      if(badge){badge.className='';badge.classList.add('live');}
      if(dsLabel)dsLabel.textContent='LIVE DATA';
      if(tooltip)tooltip.textContent='Connected to Databricks. '+cs.row_count+' plan rows from gold tables.';
    }else{
      if(badge){badge.className='';badge.classList.add('fallback');}
      if(dsLabel)dsLabel.textContent='STATIC DATA';
      if(tooltip)tooltip.textContent='Databricks unavailable — showing built-in data. '+(cs&&cs.reason?cs.reason:'timeout');
    }
  }).catch(()=>{
    if(badge){badge.className='';badge.classList.add('fallback');}
    if(dsLabel)dsLabel.textContent='STATIC DATA';
  });

  // ── Fetch all data in PARALLEL with 8s timeout each ──────────────────
  const [ss, plansData, hedisRaw, campaignsRaw, alertsRaw, gapsRaw, tvRaw] = await Promise.all([
    ft('/api/star-summary'),
    ft('/api/plans'),
    ft('/api/hedis-measures?contract_id=H3312'),
    ft('/api/campaigns'),
    ft('/api/alerts'),
    ft('/api/members/gaps?page_size=50'),
    ft('/api/team-view'),
  ]);

  // ── Star summary KPIs ─────────────────────────────────────────────────
  if(ss&&ss.total_enrollment){
    const fmtEnroll=v=>v>=1000000?(v/1000000).toFixed(1)+'M':Math.round(v/1000)+'K';
    const e=document.getElementById('exec-enrollment');
    const a=document.getElementById('exec-above-count');
    const p=document.getElementById('exec-above-pct');
    if(e)e.textContent=fmtEnroll(ss.total_enrollment);
    if(a&&ss.above_4star_count!=null)a.textContent=ss.above_4star_count;
    if(p&&ss.above_4star_pct!=null)p.textContent=Math.round(ss.above_4star_pct)+'%';
  }

  // ── Plans ─────────────────────────────────────────────────────────────
  if(plansData){
    const items=plansData.items||plansData;
    if(items&&items.length){
      contracts=items.map(p=>({
        name:p.plan_name,id:p.contract_id,state:p.state,enroll:p.enrollment,
        py:p.py_rating,proj:p.projected_rating,
        hedis:String(p.hedis_rating),cahps:String(p.cahps_rating),
        hos:String(p.hos_rating),partd:String(p.partd_rating)
      }));
      const cidSel=document.getElementById('filter-contract-id');
      if(cidSel){
        while(cidSel.options.length>1)cidSel.remove(1);
        contracts.forEach(c=>{const o=document.createElement('option');o.value=c.id;o.textContent=c.id;cidSel.appendChild(o);});
      }
      renderContracts(contracts);
    }
  }

  // ── HEDIS measures ────────────────────────────────────────────────────
  if(hedisRaw){
    const items=hedisRaw.items||hedisRaw;
    if(items&&items.length){
      hedisData=items.map(m=>({code:m.measure_code,name:m.measure_name,wt:m.weight||'1x',pct:m.current_rate,gaps:m.open_gap_count,color:m.status}));
      renderHedis();
      const totalGaps=hedisData.reduce((s,m)=>s+(m.gaps||0),0);
      const redCnt=hedisData.filter(m=>m.color==='red').length;
      const greenCnt=hedisData.filter(m=>m.color==='green').length;
      const yellowCnt=hedisData.filter(m=>m.color==='yellow').length;
      const hTotal=document.getElementById('hs-total');
      const hGaps=document.getElementById('hs-gaps');
      const hRed=document.getElementById('hs-red');
      if(hTotal)hTotal.textContent=hedisData.length;
      if(hGaps)hGaps.textContent=totalGaps.toLocaleString();
      if(hRed)hRed.textContent=redCnt;
      const allEl=document.getElementById('hf-all');
      const greenEl=document.getElementById('hf-green');
      const yellowEl=document.getElementById('hf-yellow');
      const redEl=document.getElementById('hf-red');
      if(allEl)allEl.textContent='All ('+hedisData.length+')';
      if(greenEl)greenEl.innerHTML='🟢 Green — Meets Target ('+greenCnt+')';
      if(yellowEl)yellowEl.innerHTML='🟡 Yellow — At Risk ('+yellowCnt+')';
      if(redEl)redEl.innerHTML='🔴 Red — Needs Attention ('+redCnt+')';
      const hedisBackEl=document.querySelector('#pg-hedis .back-btn');
      if(hedisBackEl)hedisBackEl.textContent='← Back to Plan Detail';
    }
  }

  // ── Campaigns ─────────────────────────────────────────────────────────
  if(campaignsRaw){
    const items=campaignsRaw.items||campaignsRaw;
    if(items&&items.length){
      campaigns=items.map(c=>({name:c.campaign_name,measure:c.measure_code,channel:c.primary_channel,members:c.member_count,proj:c.projected_closures,actual:c.actual_closures,lift:c.lift_pct!=null?'+'+c.lift_pct+'%':'—',cost:c.cost_str||('$'+Math.round(c.total_cost||0).toLocaleString()),roi:c.roi_str||(c.roi_multiplier!=null?c.roi_multiplier+'x':'—'),status:c.campaign_status}));
      renderROI();
      initAgentFilters();
    }
  }

  // ── Alerts / priority board ────────────────────────────────────────────
  if(alertsRaw){
    const pb=alertsRaw.priority_board||[];
    if(pb.length){
      priorities=pb.slice(0,9).map(p=>({name:p.measure_code+' – '+(p.measure_name||'').slice(0,18),score:Math.min(99,p.priority_score),color:p.priority_score>=80?'#dc2626':p.priority_score>=50?'#d97706':'#1D9E75'}));
      const el=document.getElementById('priority-board');
      if(el)el.innerHTML=priorities.map(p=>'<div style="margin-bottom:10px"><div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px"><span>'+p.name+'</span><span style="font-weight:700;color:'+p.color+'">'+p.score+'</span></div><div style="height:6px;background:#f3f4f6;border-radius:3px"><div style="height:100%;width:'+p.score+'%;background:'+p.color+';border-radius:3px"></div></div></div>').join('');
    }
    const alerts=alertsRaw.alerts||[];
    const alertContainer=document.getElementById('alert-list');
    if(alertContainer&&alerts.length){
      const sevClass={critical:'alert-crit',warning:'alert-warn',info:'alert-info'};
      alertContainer.innerHTML=alerts.slice(0,10).map(a=>'<div class="alert-item '+(sevClass[a.severity]||'alert-info')+'"><div><div class="alert-title">'+(a.title||a.alert_title||'')+'</div><div class="alert-body">'+(a.body||a.alert_body||'')+'</div>'+(a.meta||a.alert_meta?'<div class="alert-meta">'+(a.meta||a.alert_meta)+'</div>':'')+'</div></div>').join('');
    }
  }

  // ── Member gap list ────────────────────────────────────────────────────
  if(gapsRaw){
    const items=gapsRaw.items||gapsRaw;
    if(items&&items.length){
      mglData=items.map(m=>({name:m.display_name,age:m.age,prop:Math.round(m.propensity_score||0),measureCode:m.measure_code,measure:(m.measure_code||'')+(m.measure_name?' – '+m.measure_name:''),gap:m.gap_status,last:m.last_contact||'Never',channel:m.recommended_channel||'',pcp:m.pcp_name||'—',campaign:m.campaign_name||''}));
      renderMGL();
      const gc={open:0,partial:0,borderline:0};
      const pc={high:0,medium:0,low:0};
      mglData.forEach(m=>{const g=(m.gap||'').toLowerCase();if(gc[g]!=null)gc[g]++;const pr=m.prop||0;if(pr>75)pc.high++;else if(pr>40)pc.medium++;else pc.low++;});
      document.querySelectorAll('[data-val="open"]').forEach(el=>{const s=el.querySelector('span');if(s)s.textContent='('+gc.open+')';});
      document.querySelectorAll('[data-val="partial"]').forEach(el=>{const s=el.querySelector('span');if(s)s.textContent='('+gc.partial+')';});
      document.querySelectorAll('[data-val="borderline"]').forEach(el=>{const s=el.querySelector('span');if(s)s.textContent='('+gc.borderline+')';});
      document.querySelectorAll('[data-val="high"]').forEach(el=>{const s=el.querySelector('span');if(s)s.textContent='('+pc.high+')';});
      document.querySelectorAll('[data-val="medium"]').forEach(el=>{const s=el.querySelector('span');if(s)s.textContent='('+pc.medium+')';});
    }
  }

  // ── Team view ──────────────────────────────────────────────────────────
  if(tvRaw){
    const items=tvRaw.items||tvRaw;
    const tvEl=document.getElementById('team-view-body');
    if(tvEl&&items&&items.length){
      tvEl.innerHTML=items.map(t=>'<tr><td style="padding:8px 12px;font-size:12px;font-weight:600">'+t.department+'</td><td style="padding:8px 12px;font-size:12px">'+t.leader+'</td><td style="padding:8px 12px;font-size:12px;color:#1D9E75;font-weight:700">'+t.on_track_count+'</td><td style="padding:8px 12px;font-size:12px;color:#d97706;font-weight:700">'+t.at_risk_count+'</td><td style="padding:8px 12px;font-size:12px;color:#dc2626;font-weight:700">'+t.critical_count+'</td></tr>').join('');
    }
  }
}
initApp();
"""

if OLD_INIT:
    html = html[:OLD_INIT.start()] + NEW_INIT + html[OLD_INIT.end():]
    print("Replaced initApp with parallel version")
else:
    print("ERROR: initApp not found")

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

checks = [
    ('Promise.all', 'parallel fetches'),
    ('AbortController', 'timeout controller'),
    ('ft(\'/api/connection-status\'', 'connection status'),
    ('non-blocking', 'non-blocking badge'),
    ('ft(\'/api/plans\'', 'plans fetch'),
    ('ft(\'/api/campaigns\'', 'campaigns fetch'),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for needle, label in checks:
    print(f"{'OK' if needle in content else 'MISSING':8s} {label}")
print("Done")
