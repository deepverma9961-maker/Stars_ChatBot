import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# 1. Restore hardcoded contracts
html = html.replace('let contracts=[];', '''let contracts=[
  {name:'Health Plan Advantage Premier (HMO)',id:'H3312',state:'FL',enroll:112450,py:4.0,proj:4.0,hedis:'3.8',cahps:'4.2',hos:'4.0',partd:'4.1'},
  {name:'Lone Star Medicare Complete (HMO)',id:'H5521',state:'TX',enroll:98200,py:3.5,proj:3.5,hedis:'3.4',cahps:'3.6',hos:'3.5',partd:'3.7'},
  {name:'Pacific Care Advantage Gold (HMO)',id:'H2213',state:'CA',enroll:134800,py:4.5,proj:4.5,hedis:'4.6',cahps:'4.4',hos:'4.5',partd:'4.3'},
  {name:'Keystone Senior Plus (PPO)',id:'H6614',state:'PA',enroll:67300,py:4.0,proj:4.0,hedis:'3.9',cahps:'4.1',hos:'4.0',partd:'3.8'},
  {name:'Empire Blue Medicare (HMO)',id:'H7723',state:'NY',enroll:89100,py:3.5,proj:4.0,hedis:'3.7',cahps:'3.8',hos:'3.5',partd:'3.9'},
  {name:'Buckeye Health Advantage (D-SNP)',id:'H8812',state:'OH',enroll:54600,py:4.0,proj:4.0,hedis:'4.0',cahps:'3.9',hos:'4.0',partd:'4.2'},
  {name:'Desert Sun Medicare Plus (PPO)',id:'H9914',state:'AZ',enroll:72400,py:3.5,proj:3.5,hedis:'3.3',cahps:'3.7',hos:'3.5',partd:'3.4'},
  {name:'Peach State Senior Care (HMO)',id:'H1045',state:'GA',enroll:43200,py:3.0,proj:3.5,hedis:'3.2',cahps:'3.3',hos:'3.0',partd:'3.1'},
  {name:'Prairie Medicare Select (HMO)',id:'H2156',state:'IL',enroll:61800,py:4.0,proj:4.0,hedis:'4.1',cahps:'3.8',hos:'4.0',partd:'4.0'},
  {name:'Carolina Blue Medicare (HMO)',id:'H3267',state:'NC',enroll:48900,py:4.0,proj:4.5,hedis:'4.2',cahps:'4.3',hos:'4.0',partd:'4.1'},
  {name:'Great Lakes Senior Advantage (HMO)',id:'H4378',state:'MI',enroll:55700,py:3.5,proj:3.5,hedis:'3.6',cahps:'3.4',hos:'3.5',partd:'3.3'},
  {name:'Cascade Medicare Choice (PPO)',id:'H5489',state:'WA',enroll:38400,py:4.5,proj:4.5,hedis:'4.7',cahps:'4.3',hos:'4.5',partd:'4.4'},
  {name:'Blue Ridge Senior Select (HMO)',id:'H6590',state:'VA',enroll:44100,py:4.0,proj:4.0,hedis:'3.9',cahps:'4.0',hos:'4.0',partd:'3.9'},
  {name:'Rocky Mountain Medicare Plus (HMO)',id:'H7601',state:'CO',enroll:59000,py:4.0,proj:4.0,hedis:'4.0',cahps:'4.1',hos:'4.0',partd:'3.8'},
];''', 1)

html = html.replace(
    '// contract dropdown populated by initApp()',
    "const cidSel=document.getElementById('filter-contract-id');\ncontracts.forEach(c=>{const o=document.createElement('option');o.value=c.id;o.textContent=c.id;cidSel.appendChild(o);});"
)
html = html.replace('// renderContracts called by initApp()', 'renderContracts(contracts);')

# 2. Restore hedisData
html = html.replace('let hedisData=[];', """let hedisData=[
  {code:'HBD',name:'Diabetes Care – Blood Sugar Controlled',wt:'3×',pct:81.2,gaps:2340,color:'green'},
  {code:'CBP',name:'Controlling Blood Pressure',wt:'3×',pct:68.4,gaps:6124,color:'yellow'},
  {code:'PCR',name:'Plan All-Cause Readmissions',wt:'3×',pct:74.3,gaps:3890,color:'yellow'},
  {code:'BCS',name:'Breast Cancer Screening',wt:'1×',pct:71.8,gaps:4201,color:'yellow'},
  {code:'COL',name:'Colorectal Cancer Screening',wt:'1×',pct:66.3,gaps:5672,color:'red'},
  {code:'COA_MR',name:'Care for Older Adults – Medication Review',wt:'1×',pct:68.2,gaps:5120,color:'yellow'},
  {code:'COA_PA',name:'Care for Older Adults – Pain Assessment',wt:'1×',pct:72.1,gaps:4480,color:'yellow'},
  {code:'OMW',name:'Osteoporosis Management – Women Fracture',wt:'1×',pct:52.4,gaps:8920,color:'red'},
  {code:'EED',name:'Diabetes Care – Eye Exam',wt:'1×',pct:63.7,gaps:7891,color:'red'},
  {code:'KED',name:'Kidney Health Evaluation (Diabetes)',wt:'1×',pct:79.2,gaps:3120,color:'green'},
  {code:'MRP',name:'Medication Reconciliation Post-Discharge',wt:'1×',pct:58.6,gaps:7510,color:'red'},
  {code:'SPC',name:'Statin Therapy – Cardiovascular Disease',wt:'1×',pct:84.1,gaps:1847,color:'green'},
  {code:'TRC',name:'Transitions of Care',wt:'1×',pct:59.1,gaps:7240,color:'red'},
  {code:'AMM',name:'Antidepressant Medication Management',wt:'1×',pct:52.8,gaps:8310,color:'red'},
];""", 1)
html = html.replace('// renderHedis called by initApp()', 'renderHedis();')

# 3. Restore campaigns
html = html.replace('let campaigns=[];', """let campaigns=[
  {name:'Q3 COL Outreach',measure:'COL',channel:'SMS',members:356,proj:93,actual:87,lift:'+3.1%',cost:'$1,740',roi:'5.2x',status:'Completed'},
  {name:'SPC High-Risk Push',measure:'SPC',channel:'Call',members:246,proj:69,actual:71,lift:'+2.5%',cost:'$5,548',roi:'4.1x',status:'Completed'},
  {name:'AMM Follow-Up Wave',measure:'AMM',channel:'Call',members:183,proj:48,actual:41,lift:'+1.4%',cost:'$3,280',roi:'3.2x',status:'Completed'},
  {name:'FLU Blast',measure:'FLU',channel:'Email',members:245,proj:29,actual:34,lift:'+1.2%',cost:'$490',roi:'8.9x',status:'Completed'},
  {name:'CDC Incentive Campaign',measure:'CDC',channel:'Call',members:166,proj:46,actual:39,lift:'+1.4%',cost:'$4,175',roi:'3.5x',status:'Completed'},
  {name:'Q4 COL Push',measure:'COL',channel:'SMS',members:310,proj:80,actual:null,lift:'+2.8%',cost:'$1,240',roi:'—',status:'Active'},
  {name:'SPC Final Sweep',measure:'SPC',channel:'Call',members:200,proj:56,actual:null,lift:'+2.0%',cost:'$4,400',roi:'—',status:'Active'},
];""", 1)
html = html.replace('// renderROI called by initApp()', 'renderROI();')

# 4. Restore priorities + initial render
html = html.replace('let priorities=[];', """let priorities=[
  {name:'SPC – Statin',score:98,color:'#dc2626'},{name:'AMM – Antidepressant',score:95,color:'#dc2626'},
  {name:'CAHPS – Customer Svc',score:88,color:'#dc2626'},{name:'COL – Colorectal',score:82,color:'#d97706'},
  {name:'CDC – A1c',score:75,color:'#d97706'},{name:'MAD – Med Adherence',score:68,color:'#d97706'},
  {name:'CBP – Blood Pressure',score:42,color:'#1D9E75'},{name:'BCS – Breast Cancer',score:38,color:'#1D9E75'},
  {name:'FLU – Vaccination',score:25,color:'#1D9E75'},
];""", 1)

PRIO_RENDER = (
    "document.getElementById('priority-board').innerHTML="
    "priorities.map(p=>'<div style=\"margin-bottom:10px\">"
    "<div style=\"display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px\">"
    "<span>'+p.name+'</span>"
    "<span style=\"font-weight:700;color:'+p.color+'\">'+p.score+'</span></div>"
    "<div style=\"height:6px;background:#f3f4f6;border-radius:3px\">"
    "<div style=\"height:100%;width:'+p.score+'%;background:'+p.color+';border-radius:3px\">"
    "</div></div></div>').join('');"
)
html = html.replace('// priority board rendered by initApp()', PRIO_RENDER)

# 5. Restore mglData
html = html.replace('let mglData=[];', """let mglData=[
  {name:'James T.',age:71,prop:88,measureCode:'CDC',measure:'CDC – A1c Control',gap:'Open',last:'2 days ago',channel:'Call',pcp:'Dr. Patel',campaign:''},
  {name:'Maria L.',age:67,prop:82,measureCode:'COL',measure:'COL – Colorectal',gap:'Open',last:'2 days ago',channel:'SMS',pcp:'Dr. Kim',campaign:''},
  {name:'David K.',age:64,prop:79,measureCode:'SPC',measure:'SPC – Statin Therapy',gap:'Open',last:'2 days ago',channel:'Call',pcp:'Dr. Chen',campaign:''},
  {name:'Ruth O.',age:74,prop:76,measureCode:'AMM',measure:'AMM – Antidepressant',gap:'Partial',last:'2 days ago',channel:'Email',pcp:'Dr. Patel',campaign:''},
  {name:'Leon W.',age:73,prop:76,measureCode:'COL',measure:'COL – Colorectal',gap:'Partial',last:'2 days ago',channel:'Call',pcp:'Dr. Nair',campaign:''},
  {name:'Susan H.',age:69,prop:71,measureCode:'MAD',measure:'MAD – Med Adherence',gap:'Partial',last:'5 days ago',channel:'Portal',pcp:'Dr. Kim',campaign:''},
  {name:'George M.',age:72,prop:68,measureCode:'FLU',measure:'FLU – Vaccination',gap:'Borderline',last:'5 days ago',channel:'SMS',pcp:'Dr. Chen',campaign:''},
  {name:'Alice B.',age:65,prop:65,measureCode:'BCS',measure:'BCS – Breast Cancer',gap:'Open',last:'5 days ago',channel:'Email',pcp:'Dr. Patel',campaign:''},
  {name:'Frank R.',age:78,prop:61,measureCode:'CBP',measure:'CBP – Blood Pressure',gap:'Partial',last:'5 days ago',channel:'Call',pcp:'Dr. Nair',campaign:''},
  {name:'Helen G.',age:70,prop:55,measureCode:'SPC',measure:'SPC – Statin Therapy',gap:'Borderline',last:'Never',channel:'SMS',pcp:'Dr. Kim',campaign:''},
  {name:'Carlos P.',age:66,prop:52,measureCode:'CDC',measure:'CDC – A1c Control',gap:'Open',last:'Never',channel:'Call',pcp:'Dr. Chen',campaign:''},
  {name:'Dorothy F.',age:75,prop:48,measureCode:'COL',measure:'COL – Colorectal',gap:'Borderline',last:'Never',channel:'Email',pcp:'Dr. Patel',campaign:''},
];""", 1)
html = html.replace('// renderMGL called by initApp()', 'renderMGL();')

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
checks = [
    ('renderContracts(contracts);', 'initial renderContracts'),
    ('renderHedis();', 'initial renderHedis'),
    ('renderROI();', 'initial renderROI'),
    ('renderMGL();', 'initial renderMGL'),
    ('async function initApp', 'initApp API fetch'),
    ("fetch('/api/plans')", 'plans fetch'),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()
for needle, label in checks:
    print(f"{'OK' if needle in content else 'MISSING':8s} {label}")
print("Done")
