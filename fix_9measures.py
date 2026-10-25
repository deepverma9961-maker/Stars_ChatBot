import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    html = f.read()

# ── 1. Extend CAHPS_Q in the HTML with RDP, GNP, FLU ─────────────────────
OLD_Q_END = """    'FLU': {
      label:'',   "wave":"Wave 9 — Flu Vaccine","trigger":"Seasonal outreach · Oct–Dec 2025","target":75},
  };"""

# Hmm - CAHPS_Q and _WAVE_META are separate. Let me find where CAHPS_Q ends
OLD_Q_END2 = """    'DC':  [
        {"q":"How often did doctors explain things in a way that was easy to understand?","proxy":"Did your doctor always explain things clearly?","mapping":"Clear explanation"},
        {"q":"How often did doctors listen carefully to you?","proxy":"Did you feel your doctor listened to your concerns?","mapping":"Active listening"},
        {"q":"How often did doctors spend enough time with you?","proxy":"Did your doctor always spend enough time with you?","mapping":"Visit duration"},
    ],
  };"""

NEW_Q_END = """    'DC':  [
        {"q":"How often did doctors explain things in a way that was easy to understand?","proxy":"Did your doctor always explain things clearly?","mapping":"Clear explanation"},
        {"q":"How often did doctors listen carefully to you?","proxy":"Did you feel your doctor listened to your concerns?","mapping":"Active listening"},
        {"q":"How often did doctors spend enough time with you?","proxy":"Did your doctor always spend enough time with you?","mapping":"Visit duration"},
    ],
    'RDP': [
        {"q":"Using a number from 0–10, where 0 is the worst drug plan possible and 10 is the best, what number would you use to rate your drug plan?","proxy":"How would you rate your Part D drug plan overall (0–10)?","mapping":"Overall drug plan rating, top-box = 9–10"},
    ],
    'GNP': [
        {"q":"How often was it easy to get the prescription drugs you needed through your health plan?","proxy":"Was it always easy to get your prescription drugs?","mapping":"Prescription access ease"},
        {"q":"How often did you get the prescription drugs you needed?","proxy":"Did you always get the medications you needed?","mapping":"Medication availability"},
    ],
    'FLU': [
        {"q":"Did you get a flu vaccine between July 1, 2024 and the time you completed this survey?","proxy":"Did you receive your annual flu vaccine this season?","mapping":"Flu vaccination, top-box = Yes"},
    ],
  };"""

html = html.replace(OLD_Q_END2, NEW_Q_END, 1)

# ── 2. Add IV_DATA entries for DC, RDP, GNP, FLU ─────────────────────────
OLD_IV_END = """        {composite_code:'HPR',composite_label:'Overall Plan Rating',composite_name:'Overall Plan Rating',
         name:'Implement structured service recovery programme triggered by negative NLP sentiment',owner:'Member Experience',
         to:'Member Experience Director',send_to:'Member Experience Director',send_email:'memberexp.director@healthplan.com',
         metric:'Service recovery contact rate',current_val:'46%',target_val:'≥90%',status:'In Progress',
         headline:'Only 46% of members who express negative sentiment receive a structured service recovery outreach. This is the primary driver of low overall plan ratings.',
         wrong_metrics:['Service recovery contact rate: 46% (target ≥90%)','NPS: 28 (target ≥45)','Member retention rate: 84% (target ≥92%)','Voluntary disenrollment rate: 6.2% (target ≤4%)'],
         action:'Deploy NLP pipeline to flag all negative-sentiment interactions (calls, surveys, portal messages). Trigger 48h service recovery outreach with dedicated concierge team.',
         done:'Service recovery contact rate ≥90% within 48h for all flagged negative-sentiment interactions'},
      ];"""

NEW_IV_END = """        {composite_code:'HPR',composite_label:'Overall Plan Rating',composite_name:'Overall Plan Rating',
         name:'Implement structured service recovery programme triggered by negative NLP sentiment',owner:'Member Experience',
         to:'Member Experience Director',send_to:'Member Experience Director',send_email:'memberexp.director@healthplan.com',
         metric:'Service recovery contact rate',current_val:'46%',target_val:'≥90%',status:'In Progress',
         headline:'Only 46% of members who express negative sentiment receive a structured service recovery outreach. This is the primary driver of low overall plan ratings.',
         wrong_metrics:['Service recovery contact rate: 46% (target ≥90%)','NPS: 28 (target ≥45)','Member retention rate: 84% (target ≥92%)','Voluntary disenrollment rate: 6.2% (target ≤4%)'],
         action:'Deploy NLP pipeline to flag all negative-sentiment interactions (calls, surveys, portal messages). Trigger 48h service recovery outreach with dedicated concierge team.',
         done:'Service recovery contact rate ≥90% within 48h for all flagged negative-sentiment interactions'},
        {composite_code:'DC',composite_label:'C25',composite_name:'Doctor Communication',
         name:'Launch provider communication skills training with patient-centred scripting',owner:'Clinical Quality',
         to:'Chief Medical Officer',send_to:'Chief Medical Officer',send_email:'cmo@healthplan.com',
         metric:'Doctor communication top-box rate',current_val:'81%',target_val:'≥88%',status:'In Progress',
         headline:'Doctor communication scores are 7 points below the 88% target. Root cause is short visit durations and lack of standardised patient communication protocols.',
         wrong_metrics:['Doctor communication top-box rate: 81% (target ≥88%)','Avg visit duration: 14.2 min (target ≥18 min)','Provider turnover rate: 12% — new providers score 8pts lower on average','Patient portal adoption: 61% (target ≥75%) limits asynchronous communication'],
         action:'Roll out mandatory patient-centred communication training for all contracted PCPs. Implement post-visit communication checklist. Tie compliance to network contract renewal.',
         done:'Doctor communication top-box rate ≥88% for 8 consecutive weeks across ≥80% of PCPs'},
        {composite_code:'DC',composite_label:'C25',composite_name:'Doctor Communication',
         name:'Deploy after-visit summary automation to all in-network providers',owner:'Digital / IT',
         to:'Chief Information Officer',send_to:'Chief Information Officer',send_email:'cio@healthplan.com',
         metric:'After-visit summary delivery rate',current_val:'58%',target_val:'≥90%',status:'Not Started',
         headline:'Only 58% of members receive an after-visit summary. Members without summaries are 2.3× more likely to rate doctor communication as "Sometimes/Never adequate".',
         wrong_metrics:['After-visit summary delivery rate: 58% (target ≥90%)','Members without summaries: 2.3× more likely to give low communication score','42% of missed summaries are due to EHR configuration gaps'],
         action:'Mandate after-visit summary generation in all contracted EHR systems. Provide patient portal push notification within 2 hours of visit completion.',
         done:'After-visit summary delivery rate ≥90% within 2h for all completed visits'},
        {composite_code:'RDP',composite_label:'C31',composite_name:'Drug Plan Rating',
         name:'Reduce formulary step therapy burden via evidence-based protocol update',owner:'Pharmacy / IT',
         to:'Pharmacy Director',send_to:'Pharmacy Director',send_email:'pharmacy.director@healthplan.com',
         metric:'Formulary step therapy exception rate',current_val:'5.8%',target_val:'≤3%',status:'Not Started',
         headline:'Step therapy requirements are generating 5.8% exception requests — nearly double the target. Complex formulary rules are driving down drug plan satisfaction.',
         wrong_metrics:['Formulary step therapy exception rate: 5.8% (target ≤3%)','Average days to formulary decision: 2.8 days (target ≤1 day)','Drug plan satisfaction (0-10 rating): 7.1 (target ≥8.5)','52 drug coverage complaint calls in the past 7 days'],
         action:'Review and simplify step therapy protocols for top 20 drug classes. Implement fast-track exception approval for clinically-justified cases within 4 hours.',
         done:'Step therapy exception rate ≤3% with 4h decision turnaround for ≥90% of cases'},
        {composite_code:'GNP',composite_label:'C32',composite_name:'Getting Needed Drugs',
         name:'Implement real-time formulary alternative notification at pharmacy counter',owner:'Pharmacy / IT',
         to:'Pharmacy Director',send_to:'Pharmacy Director',send_email:'pharmacy.director@healthplan.com',
         metric:'Formulary exception approval rate',current_val:'78%',target_val:'≥90%',status:'Not Started',
         headline:'12% of prescription attempts result in denied fills without an immediate alternative offered. Members denied access to needed drugs rate the plan significantly lower.',
         wrong_metrics:['Formulary exception approval rate: 78% (target ≥90%)','Prescription fill rate: 94.2% (target ≥97%)','Mail-order adoption: 38% (target ≥50%)','44 drug access complaint calls in past 7 days'],
         action:'Build real-time formulary alternative notification API. When a drug is denied, pharmacist and member receive covered alternatives within 30 minutes via SMS/portal.',
         done:'Formulary alternative notification sent within 30 min for 95% of denied prescriptions'},
        {composite_code:'FLU',composite_label:'Flu Vaccine',composite_name:'Annual Flu Vaccine',
         name:'Deploy predictive outreach to close flu vaccination gap in high-risk members',owner:'Clinical Quality',
         to:'Director of Clinical Quality',send_to:'Director of Clinical Quality',send_email:'clinical.quality@healthplan.com',
         metric:'Flu vaccine rate',current_val:'71%',target_val:'≥80%',status:'Not Started',
         headline:'Flu vaccination rate is 9 percentage points below the 80% target. Members aged 75+ and those with chronic conditions are the highest-risk non-vaccinated segment.',
         wrong_metrics:['Flu vaccine rate: 71% (target ≥80%)','Members aged 75+ not yet vaccinated: 2,847','Vaccine outreach completion rate: 58% (target ≥75%)','Members with diabetes/COPD not vaccinated: 1,240'],
         action:'Deploy predictive outreach model to identify highest-risk unvaccinated members. Priority call + SMS campaign for members 75+ and chronic condition cohorts. Activate pharmacy-based vaccination partnerships.',
         done:'Flu vaccine rate ≥80% by Dec 31, 2025 for members aged 65+ enrolled in plan'},
        {composite_code:'FLU',composite_label:'Flu Vaccine',composite_name:'Annual Flu Vaccine',
         name:'Expand pharmacy-based flu vaccination network to close access gaps',owner:'Network Ops',
         to:'Director of Network Operations',send_to:'Director of Network Operations',send_email:'network.ops@healthplan.com',
         metric:'In-network pharmacy vaccination coverage',current_val:'44%',target_val:'≥70%',status:'Not Started',
         headline:'Only 44% of members have access to an in-network pharmacy that offers flu vaccination. Network gaps are disproportionately affecting rural and low-income zip codes.',
         wrong_metrics:['In-network pharmacy vaccination coverage: 44% (target ≥70%)','Rural members with no pharmacy within 5 miles: 1,890','Vaccine reminder call response rate: 18% (target ≥25%)'],
         action:'Contract 50 additional pharmacy locations for flu vaccine administration. Prioritise rural zip codes and ZIP codes with below-average vaccination rates. Enable telehealth voucher for home vaccination for homebound members.',
         done:'In-network pharmacy vaccination coverage ≥70% with ≤5 mile access for ≥90% of members'},
      ];"""

html = html.replace(OLD_IV_END, NEW_IV_END, 1)

with open("C:/STARS_FInal_Draft/stars_v2.html", 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
checks = [
    ("'RDP': [", "RDP questions"),
    ("'GNP': [", "GNP questions"),
    ("'FLU': [", "FLU questions"),
    ("composite_code:'DC'", "DC interventions"),
    ("composite_code:'RDP'", "RDP interventions"),
    ("composite_code:'GNP'", "GNP interventions"),
    ("composite_code:'FLU'", "FLU interventions"),
]
with open("C:/STARS_FInal_Draft/stars_v2.html", encoding='utf-8') as f:
    content = f.read()

iv_count = content.count("composite_code:'")
print(f"Total IV_DATA entries: {iv_count}")
for needle, label in checks:
    print(f"{'OK' if needle in content else 'MISSING':8s} {label}")
print("Done")
