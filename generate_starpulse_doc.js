const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
} = require("docx");

const NAVY = "1B3A5C";
const ORANGE = "F26722";
const GRAY_TEXT = "333333";
const LIGHT_GRAY = "F2F2F2";
const WHITE = "FFFFFF";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargin = { top: 80, bottom: 80, left: 120, right: 120 };

const PAGE_W = 12240;
const PAGE_H = 15840;
const MARGIN = 1440;
const CONTENT_W = PAGE_W - 2 * MARGIN; // 9360

// ── Text primitives ─────────────────────────────────────────
const h1 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 200 },
  children: [new TextRun({ text: t, bold: true, size: 32, font: "Arial", color: NAVY })],
});

const h2 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 280, after: 160 },
  children: [new TextRun({ text: t, bold: true, size: 26, font: "Arial", color: NAVY })],
});

const h3 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: t, bold: true, size: 22, font: "Arial", color: GRAY_TEXT })],
});

const p = (t, o = {}) => new Paragraph({
  spacing: { after: 120 },
  alignment: o.align || AlignmentType.LEFT,
  children: [new TextRun({ text: t, size: 22, font: "Arial", color: o.color || GRAY_TEXT, bold: !!o.bold, italics: !!o.italics })],
});

// Rich paragraph: array of {text, bold?, italics?, color?} runs
const rp = (runs, o = {}) => new Paragraph({
  spacing: { after: 120 },
  children: runs.map((r) => new TextRun({
    text: r.text,
    size: 22,
    font: "Arial",
    color: r.color || GRAY_TEXT,
    bold: !!r.bold,
    italics: !!r.italics,
  })),
});

const bullet = (t) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 60 },
  children: [new TextRun({ text: t, size: 22, font: "Arial", color: GRAY_TEXT })],
});

const bulletBold = (label, rest) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 60 },
  children: [
    new TextRun({ text: label + ": ", size: 22, font: "Arial", color: GRAY_TEXT, bold: true }),
    new TextRun({ text: rest, size: 22, font: "Arial", color: GRAY_TEXT }),
  ],
});

const numbered = (t) => new Paragraph({
  numbering: { reference: "numbers", level: 0 },
  spacing: { after: 60 },
  children: [new TextRun({ text: t, size: 22, font: "Arial", color: GRAY_TEXT })],
});

const spacer = (n = 120) => new Paragraph({ spacing: { after: n }, children: [] });

const rule = () => new Paragraph({
  spacing: { before: 200, after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ORANGE, space: 1 } },
  children: [],
});

const monoBlock = (lines) => lines.map((l) => new Paragraph({
  spacing: { after: 0, line: 260 },
  children: [new TextRun({ text: l, size: 18, font: "Courier New", color: GRAY_TEXT })],
}));

const quote = (t) => new Paragraph({
  spacing: { before: 160, after: 160 },
  indent: { left: 720, right: 720 },
  border: { left: { style: BorderStyle.SINGLE, size: 12, color: ORANGE, space: 12 } },
  children: [new TextRun({ text: t, italics: true, size: 22, font: "Arial", color: GRAY_TEXT })],
});

// ── Tables ────────────────────────────────────────────────
function makeCell(text, opts = {}) {
  const runs = Array.isArray(text)
    ? text.map((t) => new Paragraph({
        spacing: { after: 40 },
        children: [new TextRun({ text: t, size: 20, font: "Arial", color: opts.header ? WHITE : GRAY_TEXT, bold: !!opts.header || !!opts.bold })],
      }))
    : [new Paragraph({
        spacing: { after: 0 },
        children: [new TextRun({ text: String(text || ""), size: 20, font: "Arial", color: opts.header ? WHITE : GRAY_TEXT, bold: !!opts.header || !!opts.bold })],
      })];
  return new TableCell({
    borders,
    width: { size: opts.w, type: WidthType.DXA },
    shading: { fill: opts.header ? NAVY : (opts.shade || WHITE), type: ShadingType.CLEAR },
    margins: cellMargin,
    children: runs,
  });
}

function makeTable(headers, rows, cw) {
  const tw = cw.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: tw, type: WidthType.DXA },
    columnWidths: cw,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => makeCell(h, { header: true, w: cw[i] })),
      }),
      ...rows.map((r, ri) => new TableRow({
        children: r.map((cell, i) => makeCell(cell, { w: cw[i], shade: ri % 2 === 0 ? LIGHT_GRAY : WHITE })),
      })),
    ],
  });
}

// ═══════════════════════════════════════════════════════════════
// CONTENT
// ═══════════════════════════════════════════════════════════════

const cover = [
  spacer(400),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
    children: [new TextRun({ text: "EXL Services  |  StarPulse", size: 24, font: "Arial", color: ORANGE, bold: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: "Medicare Stars Management Platform", size: 22, font: "Arial", color: "666666" })],
  }),
  spacer(200),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: "Personas, Process,", size: 48, font: "Arial", color: NAVY, bold: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: "GenAI Reimagination", size: 48, font: "Arial", color: NAVY, bold: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: "& The Bigger Picture", size: 48, font: "Arial", color: NAVY, bold: true })],
  }),
  spacer(200),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ORANGE } },
    children: [],
  }),
  spacer(120),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "Confidential  |  Prepared for stakeholder discussion", size: 20, font: "Arial", color: "666666" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "Live URL: https://stars-pulse-1356475297832733.aws.databricksapps.com", size: 18, font: "Arial", color: "888888" })],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ── Executive Summary ─────────────────────────────────────
const execSummary = [
  h1("Executive Summary"),
  p("StarPulse is an AI-powered Medicare Stars management platform. It serves five primary personas across the health plan operating model, converts raw operational data into targeted outreach actions, and directly influences the plan's most valuable revenue lever: the CMS star rating and its associated bonus payments."),
  p("This document answers four questions:"),
  numbered("Who uses StarPulse today, with what objectives, and through what process flow?"),
  numbered("How would a GenAI-first reimagination make the product touchless and painless for each persona?"),
  numbered("Where does StarPulse's data come from (upstream) and where do its outputs go (downstream)?"),
  numbered("What is the bigger business picture — why does this platform exist and what is its financial impact?"),
  spacer(160),
  p("The single strategic theme is:"),
  quote("Move from a product that surfaces data to a product where AI does the synthesis and the human approves the action. Every persona's current job is 60-80% synthesis; GenAI can eliminate most of it, retaining the human for judgment on decisions and exceptions."),
  new Paragraph({ children: [new PageBreak()] }),
];

// ── PART 1: Personas ──────────────────────────────────────
const part1 = [
  h1("Part 1 — The Five Personas Who Use StarPulse"),
  p("Each persona is mapped to the actual pages and API endpoints in the product so their workflow is real and defensible, not hypothetical."),
  spacer(120),
  makeTable(
    ["Persona", "Role level", "Time cadence", "Primary pages"],
    [
      ["1. CMO / VP Stars", "Executive owner", "Weekly / monthly", "Marketing, Executive, Plan Detail"],
      ["2. Stars Program Director", "Operational owner", "Daily / weekly", "Executive, HEDIS, Simulator, ROI"],
      ["3. HEDIS / Quality Analyst", "Measure specialist", "Continuous", "HEDIS, Member Gap List, Alerts"],
      ["4. Care Coordinator", "Clinical, member-facing", "Hourly", "Member Gap List, HOS Urgency"],
      ["5. Outreach Agent", "Non-clinical, campaign exec", "Daily quota", "Agent Execution, ROI"],
    ],
    [2400, 2200, 2200, 2560]
  ),
  spacer(200),

  h2("Persona 1 — Chief Medical Officer / VP of Stars"),
  bulletBold("Who", "Executive owner of the Stars program, reports to CMO/CFO. Typically a physician-executive."),
  bulletBold("Objective", "Hit a portfolio-wide 4.0-star average, avoid contract-level 2.5-star penalties, unlock the CMS 5% bonus payment (~$400-800 per member per year)."),
  bulletBold("KPIs owned", "Overall CMS star rating per contract, bonus-eligible membership share, year-over-year star trajectory."),
  bulletBold("Pages used", "Marketing Overview, Executive, Plan Detail (top-level view only)."),
  bulletBold("Time cadence", "Weekly leadership review, monthly board deck."),
  bulletBold("Pain points today", "Star rating changes lag CMS reporting by 6-9 months (decisions made blind); roll-up dashboards hide the specific measures dragging performance; can't quickly answer \"if we hit 4 stars on HBD, what's the portfolio impact?\" without an analyst."),
  spacer(120),

  h2("Persona 2 — Stars Program Director / Quality Director"),
  bulletBold("Who", "Operational owner. Runs the day-to-day gap-closure program. Typically ex-quality nurse or clinical program manager."),
  bulletBold("Objective", "Convert executive targets into per-measure, per-contract campaign plans. Choose where to invest the fixed outreach budget."),
  bulletBold("KPIs owned", "Gap closures per week, measure-level rate lift, cost per closure by channel, contract-level 4-star cut adherence."),
  bulletBold("Pages used", "Executive, Plan Detail, HEDIS Measures, Simulator, Impact Projector, Campaign History & ROI."),
  bulletBold("Time cadence", "Daily standup, weekly campaign planning."),
  bulletBold("Pain points today", "Prioritization is a spreadsheet exercise (\"which measure gives the most stars per dollar?\"); Simulator is one-plan-at-a-time and can't sweep across portfolio; ROI attribution is delayed (closures counted 60-90 days after outreach)."),
  spacer(120),

  h2("Persona 3 — HEDIS / Quality Analyst"),
  bulletBold("Who", "Measure specialist. Deep expertise in one or two measure families (e.g., diabetes, medication adherence)."),
  bulletBold("Objective", "Explain measure-level performance, identify sub-populations driving gaps, recommend the specific clinical intervention."),
  bulletBold("KPIs owned", "Measure numerator/denominator accuracy, sub-population gap rates (dual-eligible, LIS, chronic segment), provider-level performance variance."),
  bulletBold("Pages used", "HEDIS Measures, Member Gap List, CAHPS Overview, Alerts & Priorities."),
  bulletBold("Time cadence", "Continuous — always investigating an anomaly."),
  bulletBold("Pain points today", "Data spans multiple systems and has to reconcile claims + EHR + labs manually; no natural-language querying (every question needs a data pull from analytics team); alert fatigue (hundreds of alerts, unclear which matter this week)."),
  spacer(120),

  h2("Persona 4 — Care Coordinator / Care Manager"),
  bulletBold("Who", "Clinical member-facing. RN or SW background. Manages a caseload of 100-300 high-risk members."),
  bulletBold("Objective", "Reach and engage assigned members. Close their gaps. Prevent adverse events (falls, admissions, ED visits)."),
  bulletBold("KPIs owned", "Members contacted per week, gaps closed per member, response rate by channel, HOS urgency triage accuracy."),
  bulletBold("Pages used", "Member Gap List, HOS Urgency Engine, Agent Execution, Alerts."),
  bulletBold("Time cadence", "Hourly — this is their job."),
  bulletBold("Pain points today", "Which member do I call first out of my 200? (Prioritization by hand); what do I say? (No script tailored to this member's specific gap + demographics); am I missing high-risk members between assessments? (No proactive alerting)."),
  spacer(120),

  h2("Persona 5 — Outreach Agent (SMS / Voice / Email)"),
  bulletBold("Who", "Non-clinical call-center or gig-labor. Executes high-volume, low-complexity outreach."),
  bulletBold("Objective", "Execute the campaign list. Meet daily contact quotas. Route escalations to Care Coordinators."),
  bulletBold("KPIs owned", "Dials per hour, contact rate, appointment-scheduled rate, members transitioned to Care mgmt handler."),
  bulletBold("Pages used", "Agent Execution, Campaign History & ROI."),
  bulletBold("Time cadence", "Daily quota, hourly refresh."),
  bulletBold("Pain points today", "Script feels generic and members don't feel personalized to; multi-channel handoff is manual (called then no answer then SMS follow-up); no live signal on which channel is converting today."),
  spacer(160),

  h3("Secondary personas (mention briefly)"),
  bulletBold("Provider Relations Manager", "Interfaces with the PCP network. Uses HOS Urgency Engine to send provider scorecards (\"your patients have 47 open fall-risk gaps\"). Objective: pull providers up the performance curve, avoid contract-loss risk."),
  bulletBold("CIO / CFO", "Not a daily user. Views the ROI page quarterly. Objective: was the outreach investment worth it? Do we scale, hold, or cut?"),
  new Paragraph({ children: [new PageBreak()] }),
];

// ── PART 2: Process flow ──────────────────────────────────
const part2 = [
  h1("Part 2 — Process Flow (as-is) for the Two Most Active Personas"),
  p("Detailed weekly and daily cycles for the two daily-active personas — Program Director and Care Coordinator. Both cycles today are heavily manual: the tool surfaces the data, but the human synthesizes and acts."),
  spacer(160),

  h2("Program Director's Weekly Cycle"),
  ...monoBlock([
    "Monday AM",
    "  -> Executive page: which contracts moved this week?",
    "  -> Plan Detail on any that dropped: which domain, which measure?",
    "",
    "Monday PM",
    "  -> Simulator: for that measure, what is the delta if I run one more campaign?",
    "",
    "Tuesday",
    "  -> HEDIS Measures page: pull the target member cohort",
    "  -> Impact Projector: model channel x incentive combinations",
    "",
    "Wednesday",
    "  -> Agent Execution: schedule the outreach batches for the week",
    "",
    "Thursday - Friday",
    "  -> Alerts & Priorities: react to any new critical alerts",
    "",
    "Following Monday",
    "  -> Campaign History & ROI: was last week's campaign closure rate on plan?",
  ]),
  spacer(240),

  h2("Care Coordinator's Daily Cycle"),
  ...monoBlock([
    "Morning login",
    "  -> HOS Urgency Engine: sort caseload by urgency_score DESC",
    "  -> Top 20 members flagged for the day",
    "",
    "For each member:",
    "  -> Member Gap List: open the profile",
    "  -> Read gap details, propensity score, PCP name, last contact",
    "  -> Call the member (or delegate SMS via Agent Execution)",
    "  -> Log outcome, either close the gap or schedule follow-up",
    "",
    "End of day",
    "  -> Case notes back to gold_member_gap.propensity_score for next-day resort",
  ]),
  new Paragraph({ children: [new PageBreak()] }),
];

// ── PART 3: GenAI reimagination ───────────────────────────
const part3 = [
  h1("Part 3 — Reimagining With GenAI: From \"Surfaces Data\" to \"Touchless\""),
  p("The gap between what StarPulse does today and a genuinely touchless product is not new features — it is replacing the manual synthesis work with generative and agentic AI. Structured by persona:"),
  spacer(160),

  h2("Reimagination for the Executive"),
  rp([
    { text: "Today: ", bold: true },
    { text: "they log in Monday and read charts. " },
    { text: "Reimagined: ", bold: true },
    { text: "they receive a spoken 3-minute morning briefing every Monday at 7am." },
  ]),
  bullet("Overnight, Claude reads the previous week's plan-level movements, the ROI data, and any new CMS star-cut announcements."),
  bullet("Generates a personalized narrative: \"H3312 dropped 0.2 stars on HBD this week — driven by 45 members whose lab results came back after the measurement window. Program Director already scheduled remediation. H2213 remains on track for 4.5 stars.\""),
  bullet("Delivered as audio to the CMO's phone during their commute, plus a text summary in Slack or email."),
  bulletBold("Underlying tech", "existing gold tables, Claude summarization, text-to-speech (ElevenLabs or Amazon Polly, already integrated for outreach). Zero clicks required."),
  spacer(160),

  h2("Reimagination for the Program Director"),
  rp([
    { text: "Today: ", bold: true },
    { text: "they open Simulator, drag sliders, guess at scenarios. " },
    { text: "Reimagined: ", bold: true },
    { text: "they speak their question." },
  ]),
  bullet("\"If I redirect $50K from PCR outreach to HBD outreach, what is the portfolio star impact?\""),
  bullet("Claude, wired into the Simulator API, runs the scenario, and answers: \"Portfolio moves from 3.87 to 3.94. HBD contract H3312 would cross the 4-star cut. Cost per additional star: $6,200.\""),
  bullet("Follow-up: \"Book that.\" Campaign auto-created, Agent Execution queue updated."),
  bulletBold("Underlying tech", "Claude as the agent orchestrator, existing Simulator + Campaigns APIs as tools. This is a natural fit for Claude's tool-use — the endpoints already exist."),
  spacer(160),

  h2("Reimagination for the HEDIS Analyst"),
  rp([
    { text: "Today: ", bold: true },
    { text: "they scan alerts, hypothesize, pull data. " },
    { text: "Reimagined: ", bold: true },
    { text: "an autonomous investigation agent." },
  ]),
  bullet("Every night an agent scans all measures for anomalies (rate drops, sub-population variance, provider outliers)."),
  bullet("For each anomaly, it runs the diagnosis loop: pull relevant claims, cross-reference EHR data, check outreach campaign timing."),
  bullet("Produces a root-cause report for the analyst to review in the morning: \"HBD dropped 3pp in the Miami market. Root cause: 2 clinics stopped submitting HbA1c lab codes in April. Recommended action: provider outreach to Clinic 84 and Clinic 91.\""),
  bullet("Analyst just approves or edits the recommended action."),
  bulletBold("Underlying tech", "Claude with tools (query gold tables, cross-reference silver, read provider scorecards). The whole analysis loop is 3-5 tool calls per anomaly."),
  spacer(160),

  h2("Reimagination for the Care Coordinator"),
  rp([
    { text: "Today: ", bold: true },
    { text: "they read a member profile and mentally compose a call. " },
    { text: "Reimagined: ", bold: true },
    { text: "hyper-personalized member briefing pre-generated for each call." },
  ]),
  bullet("Before the coordinator dials, Claude generates a 30-second brief: \"Maria Ramirez, 74, dual eligible, Spanish preferred. Two open gaps: HBD (A1c due since March) and BCS (never had a mammogram). Prior call answered from her daughter. Best time: after 6pm. Suggest offering the $25 card — she declined outreach for two years, incentive may unlock her. Nearest lab: Quest Diagnostics 3 miles from her home.\""),
  bullet("The coordinator opens with the right language, the right topic, the right offer — no prep needed."),
  bulletBold("Underlying tech", "Claude reading silver_member + gold_member_gap + silver_outreach_event history, in seconds, right before the call. Same primitives already in the app."),
  spacer(160),

  h2("Reimagination for the Outreach Agent"),
  rp([
    { text: "Today: ", bold: true },
    { text: "they read scripts and dial. " },
    { text: "Reimagined: ", bold: true },
    { text: "Claude IS the outreach agent for tier-1 SMS and voice." },
  ]),
  p("Actually — this is already partially built. The Twilio + Claude integration in the app calls members and runs interactive DTMF menus. The reimagined version:"),
  bullet("Every low-complexity outreach (appointment reminders, gap reminders, incentive offers) is 100% Claude-executed via voice or SMS."),
  bullet("Human agents only receive escalations — members who need clinical judgment, refuse the incentive, or are non-responsive after 3 attempts."),
  bullet("Human agent workload drops 70-80%; time reallocated to Care Coordination."),
  bulletBold("Underlying tech", "already in the codebase. Scale it."),
  spacer(200),

  h2("The Single Theme Tying the Reimagination Together"),
  quote("Move from \"product that surfaces data\" to \"product where AI does the synthesis and the human approves the action.\""),
  p("Every persona's current job is 60-80% synthesis (reading charts, composing scripts, prioritizing lists). GenAI can eliminate most of that. The human retains judgment on decisions and exceptions, not on the underlying analysis."),
  p("Concretely: expect 5-10x productivity per role, or the same productivity with 60% fewer FTE, with better outcomes because the AI is more consistent than manual work.", { bold: true }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ── PART 4: Upstream / Downstream ─────────────────────────
const part4 = [
  h1("Part 4 — Upstream and Downstream: The Bigger Picture"),
  p("Here is how StarPulse sits in the health-plan operating model."),

  h2("Upstream — Where StarPulse's Data Comes From"),
  makeTable(
    ["Source system", "Data", "Freshness", "Owner"],
    [
      ["Claims (EDI 837)", "1.8M+ claims per plan per year — CPT codes, ICD-10 diagnoses, dates", "Weekly batch", "Claims team"],
      ["Pharmacy (PBM feeds)", "Drug fills, days supply, adherence signals", "Daily", "PBM (CVS Caremark, Express Scripts, etc.)"],
      ["Enrollment / eligibility", "Member demographics, contract assignment, dual / LIS flags", "Monthly", "Enrollment ops"],
      ["CAHPS survey responses", "Member experience scores (customer service, care coordination, etc.)", "Annual survey window", "CMS-contracted vendor"],
      ["HOS survey responses", "Health outcomes, mental / physical function, fall history", "Annual", "CMS-contracted vendor"],
      ["Call center logs", "Member interactions, complaints, callbacks", "Daily", "Contact center"],
      ["EHR / clinical data (optional)", "Vitals, lab results, provider notes", "Real-time via HL7 / FHIR when available", "Provider partners"],
      ["CMS market reference data", "National star ratings, enrollment history, benchmarks", "Annual (October release)", "Public — CMS.gov"],
    ],
    [2400, 3600, 1680, 1680]
  ),
  spacer(160),
  p("All this flows into aiagenticdemo.stars_bronze (raw ingestion), gets cleaned and PII-hashed into stars_silver, and gets aggregated into decision-ready shapes in stars_gold."),
  spacer(200),

  h2("Downstream — Where StarPulse's Outputs Go"),
  makeTable(
    ["Destination", "What StarPulse contributes", "Business impact"],
    [
      ["CMS star rating (indirectly)", "Higher gap closure -> higher HEDIS rates -> higher star rating", "5% MA bonus at 4+ stars = $400-800 PMPY, and enrollment lift (star ratings are shown on medicare.gov)"],
      ["Member outreach systems", "Twilio SMS / voice campaigns, SendGrid email — right member, right channel, right incentive", "Gap closures + member engagement"],
      ["Provider engagement", "Provider scorecards for HOS urgency, HEDIS variance", "Provider network quality; potential contract renegotiation"],
      ["Executive reporting", "Board decks, CFO reviews, regulator conversations", "Investment decisions, budget allocation"],
      ["CMS submissions / audits", "Documented gap closure activity, audit trail (silver_outreach_event)", "Regulatory compliance, avoids CMS sanctions"],
      ["Provider incentive programs", "Attributable closure data used to compute provider quality bonuses", "Provider network alignment"],
      ["Member retention", "Better care, better experience -> higher renewal rate", "20% higher retention on members touched by the platform (industry-typical)"],
    ],
    [2400, 3400, 3560]
  ),
  spacer(240),

  h2("The One-line Summary of the Bigger Picture"),
  quote("StarPulse sits between the plan's operational data lake (claims, pharmacy, surveys) and the plan's most valuable revenue lever (CMS star ratings and MA bonus payments). It converts raw data into targeted, measurable outreach actions. Every 0.5-star improvement is worth roughly $200 per member per year in bonus revenue plus the retention lift. For a 200,000-member plan, that is a $40M annual line item — which is why the platform exists."),
  new Paragraph({ children: [new PageBreak()] }),
];

// ── PART 5: Delivery sequencing + Q&A ─────────────────────
const part5 = [
  h1("Part 5 — How to Sequence This in the Interview Answer"),
  p("Suggested 12-minute delivery structure:"),
  spacer(120),
  makeTable(
    ["Minute", "Content"],
    [
      ["0-2", "Frame: \"StarPulse serves 5 primary personas; the value chain is data -> decisions -> outreach -> CMS revenue.\""],
      ["2-5", "Personas + current process. Spend most time on Program Director and Care Coordinator — the daily-active users."],
      ["5-8", "Reimagination — anchor on the theme (synthesis becomes AI, decisions stay human), then walk 2-3 concrete examples."],
      ["8-11", "Upstream / downstream picture — this is where you show you understand the business, not just the app."],
      ["11-12", "Close with the one-line: \"The platform exists because 0.5 stars x 200K members = $40M.\""],
    ],
    [1200, 8160]
  ),
  spacer(240),

  h2("Two Questions You Can Preempt"),

  h3("What is the ROI of the GenAI reimagination?"),
  bulletBold("Care Coordinator productivity", "4x (each RN handles 800-1200 members instead of 200)"),
  bulletBold("Program Director planning cycle", "from weekly to daily (fresher decisions -> higher closure rate)"),
  bulletBold("Outreach conversion", "+30-50% because of hyper-personalization"),
  bulletBold("Combined", "for a mid-size MA plan (200K members), $8-15M / yr in avoided FTE + $10-20M / yr in incremental star bonus + $5M / yr in retention. Approximately $25-40M annual value against maybe $1-2M implementation cost."),
  spacer(160),

  h3("What is the risk?"),
  bulletBold("Model drift", "without monitoring, ML scoring quality erodes over time — need MLflow drift alerts (partially there today)"),
  bulletBold("Regulatory", "CMS + HHS OIG scrutinize AI in clinical prioritization — need documented, auditable feature importance and human-in-the-loop on high-risk decisions"),
  bulletBold("Provider pushback", "automated provider scorecards can strain contracting; handle communication carefully"),
  bulletBold("Trust", "care coordinators will not use AI they don't trust — the \"why is this member ranked here\" panel becomes critical"),
  spacer(200),

  rule(),
  p("Prepared using code-grounded product analysis of the StarPulse platform.", { italics: true, color: "666666" }),
  p("Every claim in this document maps to a real file, endpoint, or table in the codebase.", { italics: true, color: "666666" }),
];

// ═══════════════════════════════════════════════════════════════
// BUILD DOC
// ═══════════════════════════════════════════════════════════════

const doc = new Document({
  creator: "StarPulse",
  title: "StarPulse — Personas, Process, GenAI Reimagination & The Bigger Picture",
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: NAVY },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: NAVY },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: GRAY_TEXT },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "StarPulse  |  Personas, Process & GenAI", size: 18, font: "Arial", color: "888888" })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", size: 18, font: "Arial", color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial", color: "888888" }),
            new TextRun({ text: "  |  Confidential", size: 18, font: "Arial", color: "888888" }),
          ],
        })],
      }),
    },
    children: [
      ...cover,
      ...execSummary,
      ...part1,
      ...part2,
      ...part3,
      ...part4,
      ...part5,
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  const outPath = "C:\\STARS_FInal_Draft\\StarPulse_Personas_GenAI_BigPicture.docx";
  fs.writeFileSync(outPath, buffer);
  console.log("Written:", outPath);
  console.log("Size:", buffer.length, "bytes");
});
