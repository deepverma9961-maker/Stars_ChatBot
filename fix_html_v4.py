import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# ── 1. Add IDs to Plan Detail static elements ──────────────────────────────

# Target/Gap line
html = html.replace(
    '<div style="font-size:11px;color:#6b7280;margin-top:3px">Target: 4.5★ · Gap: 0.5★</div>',
    '<div style="font-size:11px;color:#6b7280;margin-top:3px" id="plan-target-gap">Target: 4.5★ · Gap: 0.5★</div>'
)

# Historical ratings container
html = html.replace(
    '<div class="hist-stars">',
    '<div class="hist-stars" id="plan-hist-stars">'
)

# Domain cards container
html = html.replace(
    '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px">',
    '<div id="plan-domain-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px">',
    1  # only the first occurrence (plan detail section)
)

# HEDIS table header star pill
html = html.replace(
    'HEDIS Measures<span class="pill p-amber">4.0★</span>',
    'HEDIS Measures<span class="pill p-amber" id="plan-hedis-star">4.0★</span>'
)

# CAHPS table header star pill
html = html.replace(
    'CAHPS Measures<span class="pill p-red">3.5★</span>',
    'CAHPS Measures<span class="pill p-red" id="plan-cahps-star">3.5★</span>'
)

# ── 2. Replace drillPlan with full API-driven version ─────────────────────
OLD_DRILL = re.search(r'function drillPlan\(i\)\{[\s\S]*?\n\}', html)
if OLD_DRILL:
    NEW_DRILL = r"""function drillPlan(i){
  const c=window._contracts[i];
  document.getElementById('plan-name').textContent=c.name;
  document.getElementById('plan-meta').textContent='Contract '+c.id+' · '+c.state+' · '+c.enroll.toLocaleString()+' enrolled';
  document.getElementById('plan-star').textContent=c.proj+'★';
  showPage('plan',document.querySelectorAll('.ntab')[2]);

  const starColor=r=>r>=4.5?'#1D9E75':r>=4.0?'#d97706':r>=3.5?'#d97706':'#dc2626';
  const domCls=r=>r>=4.5?'dom-card d-green':r>=4.0?'dom-card d-amber':'dom-card d-red';
  const starCls=r=>r>=4.5?'dom-star green':r>=4.0?'dom-star amber':'dom-star red';
  const pillCls=r=>r>=4.5?'pill p-green':r>=4.0?'pill p-amber':'pill p-red';

  // Fetch full plan detail (historical + domains)
  fetch('/api/plans/'+c.id).then(r=>r.json()).then(d=>{
    // Update target / gap
    const tg=document.getElementById('plan-target-gap');
    const gap=Math.max(0,(4.5-c.proj)).toFixed(1);
    if(tg)tg.textContent='Target: 4.5★ · Gap: '+gap+'★';

    // Historical ratings
    const hist=d.historical_ratings||[];
    const histEl=document.getElementById('plan-hist-stars');
    if(histEl&&hist.length){
      histEl.innerHTML=hist.map((h,idx)=>{
        const isProj=idx===hist.length-1;
        const clr=starColor(h.rating);
        const yr=isProj?'MY'+h.year+' Proj.':'MY'+h.year;
        const bg=isProj?'style="background:#fef2f2;border-color:#fecaca"':'';
        const yrStyle=isProj?'style="color:#c0392b"':'';
        const valStyle='style="color:'+clr+'"';
        return '<div class="hist-item" '+bg+'><div class="hist-yr" '+yrStyle+'>'+yr+'</div><div class="hist-val" '+valStyle+'>'+h.rating+'★</div></div>';
      }).join('');
    }

    // Domain cards
    const domains=d.domain_scores||[];
    const domEl=document.getElementById('plan-domain-grid');
    if(domEl&&domains.length){
      const domPageMap={HEDIS:"showPage('hedis',document.querySelectorAll('.ntab')[3])",CAHPS:"showPage('cahps',document.getElementById('ntab-cahps'))"};
      domEl.innerHTML=domains.map(dom=>{
        const onclick=domPageMap[dom.domain]||'';
        const cursor=onclick?'cursor:pointer':'';
        const sub=dom.on_track_count+'/'+dom.total_count+' on track'+(dom.critical_count?' · '+dom.critical_count+' critical':'');
        return '<div class="'+domCls(dom.rating)+'" onclick="'+onclick+'" style="'+cursor+'"><div class="dom-name">'+dom.domain+(dom.domain==='HEDIS'?' Clinical Quality':dom.domain==='CAHPS'?' Member Experience':dom.domain==='HOS'?' Health Outcomes':' / Pharmacy')+'</div><div class="'+starCls(dom.rating)+'">'+dom.rating+'★</div><div style="font-size:10px;color:#6b7280;margin-top:3px">'+sub+'</div><div style="font-size:11px;color:#c0392b;margin-top:8px;font-weight:600">View measures →</div></div>';
      }).join('');
    }

    // Update HEDIS/CAHPS header star pills
    const hedisRating=(domains.find(d=>d.domain==='HEDIS')||{}).rating||c.hedis;
    const cahpsRating=(domains.find(d=>d.domain==='CAHPS')||{}).rating||c.cahps;
    const hStar=document.getElementById('plan-hedis-star');
    const cStar=document.getElementById('plan-cahps-star');
    if(hStar){hStar.textContent=hedisRating+'★';hStar.className=pillCls(hedisRating);}
    if(cStar){cStar.textContent=cahpsRating+'★';cStar.className=pillCls(cahpsRating);}
  }).catch(()=>{});

  // Fetch live HEDIS measures for this plan
  fetch('/api/hedis-measures?contract_id='+c.id).then(r=>r.json()).then(data=>{
    const items=data.items||data;
    const statusMap={green:'ok',yellow:'risk',red:'crit'};
    if(items&&items.length){
      document.getElementById('plan-hedis-body').innerHTML=items.slice(0,8).map(m=>rowTr({
        code:m.measure_code,name:(m.measure_name||'').slice(0,28),
        pct:m.current_rate,status:statusMap[m.status]||'ok'
      })).join('');
    }
  }).catch(()=>{});

  // Fetch live CAHPS for this plan
  fetch('/api/cahps?contract_id='+c.id).then(r=>r.json()).then(data=>{
    const composites=data.composites||[];
    if(composites.length){
      document.getElementById('plan-cahps-body').innerHTML=composites.map(m=>rowTr({
        code:m.composite_code,name:(m.composite_name||'').slice(0,28),
        pct:Math.round(m.current_pct||0),
        status:m.status==='ok'?'ok':m.status==='risk'?'risk':'crit'
      })).join('');
    }
  }).catch(()=>{});
}"""
    html = html[:OLD_DRILL.start()] + NEW_DRILL + html[OLD_DRILL.end():]

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
checks = [
    ('plan-target-gap', 'target-gap id'),
    ('plan-hist-stars', 'hist-stars id'),
    ('plan-domain-grid', 'domain-grid id'),
    ('plan-hedis-star', 'hedis-star id'),
    ('plan-cahps-star', 'cahps-star id'),
    ("fetch('/api/plans/'+c.id)", 'plan detail fetch'),
    ('historical_ratings', 'historical ratings update'),
    ('domain_scores', 'domain scores update'),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for needle, label in checks:
    print(f"{'OK' if needle in content else 'MISSING':8s} {label}")
print("Done")
