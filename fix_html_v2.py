import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# ── 1. Add IDs to hardcoded HEDIS summary stats ────────────────────────────
html = html.replace(
    '<div class="hs-val">14</div><div class="hs-sub">HEDIS clinical measures</div>',
    '<div class="hs-val" id="hs-total">14</div><div class="hs-sub">HEDIS clinical measures</div>'
)
html = html.replace(
    '<div class="hs-val">77,175</div><div class="hs-sub">estimated open gaps</div>',
    '<div class="hs-val" id="hs-gaps">77,175</div><div class="hs-sub">estimated open gaps</div>'
)
html = html.replace(
    '<div class="hs-val" style="color:#dc2626">8</div><div class="hs-sub">need urgent attention</div>',
    '<div class="hs-val" id="hs-red" style="color:#dc2626">8</div><div class="hs-sub">need urgent attention</div>'
)

# ── 2. Replace drillPlan to fetch live plan-specific data ──────────────────
OLD_DRILL = """function drillPlan(i){
  const c=window._contracts[i];
  document.getElementById('plan-name').textContent=c.name;
  document.getElementById('plan-meta').textContent='Contract '+c.id+' · '+c.state+' · '+c.enroll.toLocaleString()+' enrolled';
  document.getElementById('plan-star').textContent=c.proj+'★';
  showPage('plan',document.querySelectorAll('.ntab')[2]);
}"""

NEW_DRILL = """function drillPlan(i){
  const c=window._contracts[i];
  document.getElementById('plan-name').textContent=c.name;
  document.getElementById('plan-meta').textContent='Contract '+c.id+' · '+c.state+' · '+c.enroll.toLocaleString()+' enrolled';
  document.getElementById('plan-star').textContent=c.proj+'\\u2605';
  showPage('plan',document.querySelectorAll('.ntab')[2]);
  // Fetch live plan-specific HEDIS
  fetch('/api/hedis-measures?contract_id='+c.id).then(r=>r.json()).then(data=>{
    const items=data.items||data;
    const statusMap={green:'ok',yellow:'risk',red:'crit'};
    document.getElementById('plan-hedis-body').innerHTML=items.slice(0,8).map(m=>rowTr({
      code:m.measure_code,name:m.measure_name.slice(0,28),
      pct:m.current_rate,status:statusMap[m.status]||'ok'
    })).join('');
  }).catch(()=>{});
  // Fetch live CAHPS for this plan
  fetch('/api/cahps?contract_id='+c.id).then(r=>r.json()).then(data=>{
    const composites=data.composites||[];
    if(composites.length){
      document.getElementById('plan-cahps-body').innerHTML=composites.map(m=>rowTr({
        code:m.composite_code,name:m.composite_name.slice(0,28),
        pct:Math.round(m.current_pct||0),
        status:m.status==='ok'?'ok':m.status==='risk'?'risk':'crit'
      })).join('');
    }
  }).catch(()=>{});
}"""

html = html.replace(OLD_DRILL, NEW_DRILL, 1)

# ── 3. Replace the entire existing initApp() with a comprehensive version ─
# Remove old initApp + initApp() call
html = re.sub(
    r'async function initApp\(\)\{[\s\S]*?\}\s*initApp\(\);',
    '// initApp replaced below',
    html
)

FULL_INIT = '''
async function initApp(){
  // ── Star summary KPIs ────────────────────────────────────────────────────
  try{
    const ss=await fetch('/api/star-summary').then(r=>r.json());
    const fmtEnroll=v=>v>=1000000?(v/1000000).toFixed(1)+'M':Math.round(v/1000)+'K';
    const e=document.getElementById('exec-enrollment');
    const a=document.getElementById('exec-above-count');
    const p=document.getElementById('exec-above-pct');
    if(e&&ss.total_enrollment)e.textContent=fmtEnroll(ss.total_enrollment);
    if(a&&ss.above_4star_count!=null)a.textContent=ss.above_4star_count;
    if(p&&ss.above_4star_pct!=null)p.textContent=Math.round(ss.above_4star_pct)+'%';
  }catch(e){console.warn('star-summary:',e);}

  // ── Plans ────────────────────────────────────────────────────────────────
  try{
    const data=await fetch('/api/plans').then(r=>r.json());
    const items=data.items||data;
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
  }catch(e){console.warn('plans:',e);}

  // ── HEDIS measures (default H3312) ───────────────────────────────────────
  try{
    const data=await fetch('/api/hedis-measures?contract_id=H3312').then(r=>r.json());
    const items=data.items||data;
    if(items&&items.length){
      hedisData=items.map(m=>({
        code:m.measure_code,name:m.measure_name,
        wt:m.weight||'1x',pct:m.current_rate,
        gaps:m.open_gap_count,color:m.status
      }));
      renderHedis();
      // Update HEDIS summary stats
      const totalGaps=hedisData.reduce((s,m)=>s+(m.gaps||0),0);
      const redCnt=hedisData.filter(m=>m.color==='red').length;
      const hTotal=document.getElementById('hs-total');
      const hGaps=document.getElementById('hs-gaps');
      const hRed=document.getElementById('hs-red');
      if(hTotal)hTotal.textContent=hedisData.length;
      if(hGaps)hGaps.textContent=totalGaps.toLocaleString();
      if(hRed)hRed.textContent=redCnt;
      // Update filter counts
      const gCnt=hedisData.filter(m=>m.color==='green').length;
      const yCnt=hedisData.filter(m=>m.color==='yellow').length;
      const greenEl=document.getElementById('hf-green');
      const yellowEl=document.getElementById('hf-yellow');
      const redEl=document.getElementById('hf-red');
      const allEl=document.getElementById('hf-all');
      if(allEl)allEl.textContent='All ('+hedisData.length+')';
      if(greenEl)greenEl.innerHTML='\\uD83D\\uDFE2 Green \\u2014 Meets Target ('+gCnt+')';
      if(yellowEl)yellowEl.innerHTML='\\uD83D\\uDFE1 Yellow \\u2014 At Risk ('+yCnt+')';
      if(redEl)redEl.innerHTML='\\uD83D\\uDD34 Red \\u2014 Needs Attention ('+redCnt+')';
    }
  }catch(e){console.warn('hedis:',e);}

  // ── Campaigns ────────────────────────────────────────────────────────────
  try{
    const data=await fetch('/api/campaigns').then(r=>r.json());
    const items=data.items||data;
    if(items&&items.length){
      campaigns=items.map(c=>({
        name:c.campaign_name,measure:c.measure_code,channel:c.primary_channel,
        members:c.member_count,proj:c.projected_closures,actual:c.actual_closures,
        lift:c.lift_pct!=null?'+'+c.lift_pct+'%':'—',
        cost:c.cost_str||('$'+Math.round(c.total_cost||0).toLocaleString()),
        roi:c.roi_str||(c.roi_multiplier!=null?c.roi_multiplier+'x':'—'),
        status:c.campaign_status
      }));
      renderROI();
      initAgentFilters();
    }
  }catch(e){console.warn('campaigns:',e);}

  // ── Alerts / priority board ───────────────────────────────────────────────
  try{
    const data=await fetch('/api/alerts').then(r=>r.json());
    const pb=data.priority_board||[];
    if(pb.length){
      priorities=pb.slice(0,9).map(p=>({
        name:p.measure_code+' \\u2013 '+(p.measure_name||'').slice(0,18),
        score:Math.min(99,p.priority_score),
        color:p.priority_score>=80?'#dc2626':p.priority_score>=50?'#d97706':'#1D9E75'
      }));
      const el=document.getElementById('priority-board');
      if(el)el.innerHTML=priorities.map(p=>'<div style="margin-bottom:10px"><div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px"><span>'+p.name+'</span><span style="font-weight:700;color:'+p.color+'">'+p.score+'</span></div><div style="height:6px;background:#f3f4f6;border-radius:3px"><div style="height:100%;width:'+p.score+'%;background:'+p.color+';border-radius:3px"></div></div></div>').join('');
    }
    // Also update alert items if visible
    const alerts=data.alerts||[];
    const alertContainer=document.getElementById('alert-list');
    if(alertContainer&&alerts.length){
      const sevClass={critical:'alert-crit',warning:'alert-warn',info:'alert-info'};
      alertContainer.innerHTML=alerts.slice(0,10).map(a=>'<div class="alert-item '+(sevClass[a.severity]||'alert-info')+'"><div><div class="alert-title">'+(a.title||a.alert_title||'')+'</div><div class="alert-body">'+(a.body||a.alert_body||'')+'</div>'+(a.meta||a.alert_meta?'<div class="alert-meta">'+(a.meta||a.alert_meta)+'</div>':'')+'</div></div>').join('');
    }
  }catch(e){console.warn('alerts:',e);}

  // ── Member gap list ───────────────────────────────────────────────────────
  try{
    const data=await fetch('/api/members/gaps?page_size=50').then(r=>r.json());
    const items=data.items||data;
    if(items&&items.length){
      mglData=items.map(m=>({
        name:m.display_name,age:m.age,prop:Math.round(m.propensity_score||0),
        measureCode:m.measure_code,
        measure:(m.measure_code||'')+(m.measure_name?' \\u2013 '+m.measure_name:''),
        gap:m.gap_status,last:m.last_contact||'Never',
        channel:m.recommended_channel||'',pcp:m.pcp_name||'\\u2014',
        campaign:m.campaign_name||''
      }));
      renderMGL();
      // Update gap/propensity counts for simulator
      const gc={open:0,partial:0,borderline:0};
      const pc={high:0,medium:0,low:0};
      mglData.forEach(m=>{
        const g=(m.gap||'').toLowerCase();
        if(gc[g]!=null)gc[g]++;
        const pr=m.prop||0;
        if(pr>75)pc.high++;else if(pr>40)pc.medium++;else pc.low++;
      });
      // Update simulator chip counts
      document.querySelectorAll('[data-val="open"]').forEach(el=>{
        const s=el.querySelector('span');if(s)s.textContent='('+gc.open+')';
      });
      document.querySelectorAll('[data-val="partial"]').forEach(el=>{
        const s=el.querySelector('span');if(s)s.textContent='('+gc.partial+')';
      });
      document.querySelectorAll('[data-val="borderline"]').forEach(el=>{
        const s=el.querySelector('span');if(s)s.textContent='('+gc.borderline+')';
      });
      document.querySelectorAll('[data-val="high"]').forEach(el=>{
        const s=el.querySelector('span');if(s)s.textContent='('+pc.high+')';
      });
      document.querySelectorAll('[data-val="medium"]').forEach(el=>{
        const s=el.querySelector('span');if(s)s.textContent='('+pc.medium+')';
      });
    }
  }catch(e){console.warn('members/gaps:',e);}

  // ── Team view (used in CAHPS/team tab if present) ─────────────────────────
  try{
    const data=await fetch('/api/team-view').then(r=>r.json());
    const items=data.items||data;
    const tvEl=document.getElementById('team-view-body');
    if(tvEl&&items&&items.length){
      tvEl.innerHTML=items.map(t=>'<tr><td style="padding:8px 12px;font-size:12px;font-weight:600">'+t.department+'</td><td style="padding:8px 12px;font-size:12px">'+t.leader+'</td><td style="padding:8px 12px;font-size:12px;color:#1D9E75;font-weight:700">'+t.on_track_count+'</td><td style="padding:8px 12px;font-size:12px;color:#d97706;font-weight:700">'+t.at_risk_count+'</td><td style="padding:8px 12px;font-size:12px;color:#dc2626;font-weight:700">'+t.critical_count+'</td></tr>').join('');
    }
  }catch(e){}
}
initApp();
'''

html = html.replace('// initApp replaced below', FULL_INIT)

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
checks = [
    ('async function initApp', 'initApp present'),
    ("fetch('/api/star-summary')", 'star-summary'),
    ("fetch('/api/plans')", 'plans'),
    ("fetch('/api/hedis-measures", 'hedis'),
    ("fetch('/api/campaigns')", 'campaigns'),
    ("fetch('/api/alerts')", 'alerts'),
    ("fetch('/api/members/gaps", 'member gaps'),
    ("fetch('/api/team-view')", 'team-view'),
    ("fetch('/api/hedis-measures?contract_id='+c.id)", 'per-plan hedis'),
    ("fetch('/api/cahps?contract_id='+c.id)", 'per-plan cahps'),
    ('id="hs-total"', 'hs-total id'),
    ('id="hs-gaps"', 'hs-gaps id'),
    ('id="hs-red"', 'hs-red id'),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for needle, label in checks:
    print(f"{'OK' if needle in content else 'MISSING':8s} {label}")
print("Done")
