const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak, TabStopType, TabStopPosition
} = require("docx");

const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1440, CONTENT_W = PAGE_W - 2 * MARGIN;
const BLUE = "1B3A5C", ORANGE = "F26722", LIGHT_GRAY = "F2F2F2", WHITE = "FFFFFF";
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cm = { top: 60, bottom: 60, left: 100, right: 100 };

function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text: t, bold: true, size: 36, font: "Arial", color: BLUE })] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text: t, bold: true, size: 28, font: "Arial", color: BLUE })] }); }
function h3(t) { return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text: t, bold: true, size: 24, font: "Arial", color: "333333" })] }); }
function p(t, o = {}) { return new Paragraph({ spacing: { after: 120 }, alignment: o.align || AlignmentType.LEFT, children: [new TextRun({ text: t, size: 22, font: "Arial", color: o.color || "333333", bold: !!o.bold, italics: !!o.italics })] }); }
function bullet(t) { return new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: t, size: 22, font: "Arial", color: "333333" })] }); }
function bb(l, d) { return new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: l + ": ", size: 22, font: "Arial", color: "333333", bold: true }), new TextRun({ text: d, size: 22, font: "Arial", color: "333333" })] }); }
function mono(lines) { return lines.map(l => new Paragraph({ spacing: { after: 0, line: 260 }, children: [new TextRun({ text: l, size: 17, font: "Courier New", color: "333333" })] })); }
function sp(n = 120) { return new Paragraph({ spacing: { after: n }, children: [] }); }
function pb() { return new Paragraph({ children: [new PageBreak()] }); }

function makeRow(cells, o = {}) {
  return new TableRow({ children: cells.map(c => new TableCell({ borders, width: { size: c.w, type: WidthType.DXA }, shading: { fill: o.header ? BLUE : (o.shade || WHITE), type: ShadingType.CLEAR }, margins: cm, verticalAlign: "center", children: [new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: c.t || "", size: 20, font: "Arial", bold: !!o.header || !!c.bold, color: o.header ? WHITE : "333333" })] })] })) });
}
function tbl(headers, rows, cw) {
  const tw = cw.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: tw, type: WidthType.DXA }, columnWidths: cw, rows: [
    makeRow(headers.map((h, i) => ({ t: h, w: cw[i] })), { header: true }),
    ...rows.map((r, ri) => makeRow(r.map((t, i) => ({ t, w: cw[i] })), { shade: ri % 2 === 0 ? LIGHT_GRAY : WHITE }))
  ]});
}

// ── COVER PAGE ──────────────────────────────────────────────────────────────
function cover() {
  return [
    sp(500),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [new TextRun({ text: "EXL Services | StarPulse", size: 28, font: "Arial", color: ORANGE, bold: true })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "Medicare Stars Management Platform", size: 24, font: "Arial", color: "666666" })] }),
    sp(160),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Architecture, ML & GenAI", size: 52, font: "Arial", color: BLUE, bold: true })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Technical Reference", size: 36, font: "Arial", color: BLUE })] }),
    sp(80),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "AI-Powered Stars Performance Intelligence", size: 28, font: "Arial", color: ORANGE })] }),
    sp(300),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: ORANGE } }, children: [] }),
    sp(80),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Version 1.0  |  May 2026  |  Confidential", size: 22, font: "Arial", color: "888888" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Prepared by: EXL Health Analytics & AI Practice", size: 22, font: "Arial", color: "888888" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Platform: Databricks Lakehouse  |  Deployment: Databricks Apps (AWS)", size: 20, font: "Arial", color: "999999" })] }),
    sp(200),
    tbl(["Property", "Value"], [
      ["Document ID", "ARCH-ML-STARPULSE-2026-001"],
      ["Classification", "Confidential - Internal Use"],
      ["Scope", "Architecture + ML + GenAI Reference"],
      ["Live URL", "https://stars-pulse-1356475297832733.aws.databricksapps.com"],
      ["Catalog", "aiagenticdemo (Unity Catalog)"],
    ], [3000, 6360]),
    pb(),
  ];
}

// ── SECTION 1: SOLUTION ARCHITECTURE ────────────────────────────────────────
function archSection() {
  return [
    h1("1. Solution Architecture"),

    h2("1.1 Architecture Overview"),
    p("StarPulse is built on the Databricks Lakehouse with a Medallion data architecture (Bronze/Silver/Gold), FastAPI REST backend, and a single-page React application. The platform manages 14 health plan contracts, 45 quality measures, and ~980K members."),
    sp(40),
    ...mono([
      "+===========================================================================+",
      "|                    StarPulse Solution Architecture                         |",
      "+===========================================================================+",
      "|                                                                           |",
      "|  +-------------------+   +-------------------------------------------+   |",
      "|  | Source Systems    |   |        Databricks Lakehouse                |   |",
      "|  |  - Claims (EDI)  |   |  +--------+  +--------+  +--------+       |   |",
      "|  |  - Pharmacy (PBM)|-->|  | Bronze |->| Silver |->|  Gold  |       |   |",
      "|  |  - CAHPS Survey  |   |  | 5 tbls |  | 9 tbls |  | 12 tbls|       |   |",
      "|  |  - Call Center   |   |  +--------+  +--------+  +--------+       |   |",
      "|  |  - Enrollment    |   |       |           |            |           |   |",
      "|  +-------------------+   |  +----+----+ +---+-----+ +---+------+    |   |",
      "|                          |  | Workflows| | Feature | | ML Model|    |   |",
      "|                          |  | (Daily)  | | Store   | | Serving |    |   |",
      "|                          |  +----------+ +---------+ +----------+   |   |",
      "|                          |       |            |            |         |   |",
      "|                          |  +----+------------+------------+----+    |   |",
      "|                          |  |    SQL Warehouse (Serverless)     |    |   |",
      "|                          |  +----------------------------------+    |   |",
      "|                          +-------------------------------------------+   |",
      "|                                          |                               |",
      "|  +-------------------+          +--------+--------+                      |",
      "|  | External Services |          |  FastAPI Backend |                     |",
      "|  |  - Twilio (SMS)   |<---------|  13 routers      |                     |",
      "|  |  - SendGrid(Email)|          |  18 endpoints    |                     |",
      "|  +-------------------+          +---------+--------+                     |",
      "|                                           |                              |",
      "|                                  +--------+--------+                     |",
      "|                                  |  React SPA      |                     |",
      "|                                  |  14 pages       |                     |",
      "|                                  |  Chart.js       |                     |",
      "|                                  +-----------------+                     |",
      "+===========================================================================+",
    ]),
    pb(),

    h2("1.2 Technology Stack"),
    tbl(
      ["Layer", "Technology", "Details"],
      [
        ["Compute", "Databricks Runtime 14.3", "Spark 3.5.0, Scala 2.12, m5d.large x 2 workers"],
        ["Storage", "Delta Lake", "ACID transactions, time travel, Unity Catalog managed"],
        ["Catalog", "Unity Catalog", "aiagenticdemo: stars_bronze / stars_silver / stars_gold schemas"],
        ["SQL Engine", "SQL Warehouse", "Serverless, Photon-accelerated, auto-scaling"],
        ["Orchestration", "Databricks Workflows", "14-task DAG, daily 6:00 AM ET, auto-retry"],
        ["API", "FastAPI 0.111 + Uvicorn 0.29", "13 routers, 18 endpoints, Pydantic v2"],
        ["DB Connector", "databricks-sql-connector 3.4", "ODBC/Thrift to SQL Warehouse"],
        ["Frontend", "React 18 (SPA)", "Chart.js 4.4, TanStack Query, self-contained HTML"],
        ["Outreach", "Twilio + SendGrid", "SMS and email for member gap closure campaigns"],
        ["Deployment", "Databricks Apps", "Serverless, AWS-hosted, auto-TLS"],
      ],
      [2000, 3200, 4160]
    ),
    sp(80),

    h2("1.3 Data Architecture (Medallion)"),
    ...mono([
      "BRONZE (Raw)                 SILVER (Curated)              GOLD (Analytics)",
      "========================     ==========================    ========================",
      "",
      "bronze_enrollment_raw   -->  silver_member (PII hashed)    gold_star_rating_summary",
      "  100K members               silver_plan (28 contracts)    gold_measure_scorecard",
      "                             silver_provider (12K)         gold_member_gap (~260K)",
      "",
      "bronze_claims_raw       -->  silver_claim (~1.8M)          gold_cahps_overview",
      "  1.8M claims                 (partitioned by month)       gold_campaign_performance",
      "                                                           gold_alert_priority",
      "bronze_pharmacy_raw     -->  silver_pharmacy_fill (~1.1M)  gold_intervention_hub",
      "  1.1M Rx fills               (partitioned by month)       gold_team_view",
      "",
      "bronze_cahps_survey_raw -->  silver_cahps_response         gold_hos_measures (5)",
      "  ~120K responses             (top-box computed)           gold_hos_scorecard (70)",
      "                             silver_measure (45)           gold_hos_members (~14K)",
      "bronze_call_center_raw  -->  silver_outreach_event (~120K) gold_hos_provider (1K)",
      "  375K calls                 silver_call_event (~375K)",
      "                                                           MARKET REF (stars_gold)",
      "TOTAL: 3.3M rows            TOTAL: 3.6M+ rows             cms_plan_enrollment",
      "                                                           cms_plan_star_history",
      "                                                           cms_measure_star_hist",
    ]),
    sp(80),

    h2("1.4 API Architecture"),
    tbl(
      ["Router", "Endpoints", "Backing Tables"],
      [
        ["star_summary", "GET /api/star-summary", "gold_star_rating_summary"],
        ["plans", "GET /api/plans, /plans/{id}", "gold_star_rating_summary + silver_plan"],
        ["hedis", "GET /api/hedis-measures", "gold_measure_scorecard + silver_measure"],
        ["cahps", "GET /api/cahps, /cahps/pulse", "gold_cahps_overview + silver_cahps_response"],
        ["members", "GET /api/members/gaps, /members/{key}", "gold_member_gap + silver_member"],
        ["campaigns", "GET /api/campaigns", "gold_campaign_performance"],
        ["alerts", "GET /api/alerts", "gold_alert_priority"],
        ["simulator", "POST /api/simulator/run", "gold_measure_scorecard"],
        ["hos", "GET /api/hos/measures, /members, /providers", "gold_hos_* (4 tables)"],
        ["market", "GET /api/market/enrollment, /plan-stars", "stars_gold.cms_* (3 tables)"],
        ["outreach", "POST /api/outreach/send-bundle", "Twilio + SendGrid"],
      ],
      [1800, 3600, 3960]
    ),
    sp(40),
    p("Every endpoint implements graceful degradation: attempt Databricks SQL query, catch exceptions, return in-memory fallback data with a degradation flag. Zero-downtime UX guaranteed."),
    sp(40),

    h2("1.5 Pipeline Orchestration DAG"),
    ...mono([
      "stars_medallion_pipeline  |  Daily 6:00 AM ET  |  Spark 14.3  |  m5d.large x 2",
      "",
      "  01_enrollment ---+                                     09_star_ratings",
      "                   +--> 06_member_plan ----+-----------> 10_measure_scorecard",
      "  02_claims -----+                   |    |          +-> 11_member_gaps",
      "  03_pharmacy ---+--> 08_clinical ---+    +-------+  |   12_cahps_teamview",
      "  05_call_ctr ---+      events       |    |       |  +-> 13_campaigns_alerts",
      "                                     |    |       +----> 14_hos",
      "  04_cahps -------> 07_measure_cahps-+----+",
      "",
      "  Legend:  ---> dependency    +--> fan-out    Numbers = notebook IDs",
    ]),
    sp(40),
    p("Bronze tasks run in parallel (~5 min). Silver layer depends on Bronze completions. Gold tasks fan out from Silver outputs. Full pipeline completes in ~25 minutes."),

    h2("1.6 Entity Relationship Diagram"),
    ...mono([
      "+------------------+     +-------------------+     +---------------------+",
      "| silver_plan      |     | silver_measure    |     | silver_provider     |",
      "| PK: plan_key     |<-+  | PK: measure_key   |<-+  | PK: provider_key    |",
      "| contract_id      |  |  | measure_code      |  |  | npi, specialty      |",
      "| plan_name, state |  |  | category, weight  |  |  +---------------------+",
      "+------------------+  |  +-------------------+  |            ^",
      "        ^             |           ^             |            |",
      "        |             |           |             |   +--------+--------+",
      "        |  +----------+-----------+----------+  |   | silver_member   |",
      "        |  |    gold_measure_scorecard       |  |   | PK: member_key  |",
      "        |  |    FK: plan_key, measure_key    |  |   | FK: pcp_provider|",
      "        |  |    current_rate, status, target  |  |   | display_name   |",
      "        |  +--------------------------------+  |   | age, segment    |",
      "        |                                      |   +--------+--------+",
      "        |  +------------------+                |            |",
      "        +--| gold_star_rating |                |   +--------+--------+",
      "        |  | FK: plan_key     |                |   | gold_member_gap |",
      "        |  | star ratings     |                +---| FK: measure_key |",
      "        |  +------------------+                    | FK: plan_key    |",
      "        |                                          | FK: member_key  |",
      "        +------------------------------------------| propensity,     |",
      "                                                   | channel, status |",
      "                                                   +-----------------+",
    ]),
    pb(),
  ];
}

// ── SECTION 2: ML & AI COMPONENTS ───────────────────────────────────────────
function mlSection() {
  return [
    h1("2. Machine Learning & AI Components"),

    h2("2.1 Analytical Foundation (Operational Baseline)"),
    p("StarPulse implements a rule-based analytical engine as the operational baseline. The architecture is designed to accommodate trained ML models as they mature through the development lifecycle."),

    h3("Star Rating Calculator"),
    p("star_calculator.py computes weighted overall star ratings. 14 HEDIS measures, each with CMS weight, 4-star/5-star thresholds:"),
    tbl(
      ["Measure", "Wt", "4-Star", "5-Star", "Status Logic"],
      [
        ["HBD (Blood Sugar)", "3x", "80.0%", "90.0%", "G>=85, Y>=72, R<72"],
        ["CBP (Blood Pressure)", "3x", "70.0%", "80.0%", "G>=75, Y>=62, R<62"],
        ["PCR (Readmissions)", "3x", "75.0%", "85.0%", "G>=80, Y>=67, R<67"],
        ["BCS (Breast Cancer)", "1x", "72.0%", "82.0%", "G>=77, Y>=64, R<64"],
        ["COL (Colorectal)", "1x", "68.0%", "78.0%", "G>=73, Y>=60, R<60"],
        ["COA_MR (Medication Review)", "1x", "82.0%", "90.0%", "G>=87, Y>=74, R<74"],
        ["COA_PA (Pain Assessment)", "1x", "74.0%", "84.0%", "G>=79, Y>=66, R<66"],
        ["OMW (Osteoporosis)", "1x", "62.0%", "72.0%", "G>=67, Y>=54, R<54"],
        ["EED (Eye Exam)", "1x", "70.0%", "80.0%", "G>=75, Y>=62, R<62"],
        ["KED (Kidney Eval)", "1x", "65.0%", "75.0%", "G>=70, Y>=57, R<57"],
        ["MRP (Med Reconciliation)", "1x", "86.0%", "94.0%", "G>=91, Y>=78, R<78"],
        ["SPC (Statin Therapy)", "1x", "68.0%", "78.0%", "G>=73, Y>=60, R<60"],
        ["TRC (Transitions of Care)", "1x", "70.0%", "80.0%", "G>=75, Y>=62, R<62"],
        ["AMM (ED Follow-up)", "1x", "64.0%", "74.0%", "G>=69, Y>=56, R<56"],
      ],
      [2200, 600, 1400, 1400, 3760]
    ),
    sp(40),
    p("Formula: overall_star = ROUND( SUM(measure_stars * weight) / SUM(weight) , nearest 0.5 )"),
    sp(40),

    h3("Simulator Engine"),
    p("simulator_engine.py projects gap closure outcomes based on channel, incentive, and member filtering:"),
    tbl(
      ["Parameter", "Values"],
      [
        ["Baseline Closure Rates", "Call: 28%  |  SMS: 22%  |  Email: 12%"],
        ["Incentive Boost", "None: +0%  |  $25 gift card: +4%  |  $50 gift card: +8%"],
        ["Cost per Member", "Call: $22  |  SMS: $4  |  Email: $2  (+ incentive cost)"],
        ["Waterfall (4-week rollout)", "Week 1: 40%  |  Week 2: 30%  |  Week 3: 20%  |  Week 4: 10%"],
        ["Gap Weights", "Open: 55%  |  Partial: 30%  |  Borderline: 15%"],
        ["Propensity Weights", "High: 25%  |  Medium: 42%  |  Low: 33%"],
        ["Suppressions", "Recently contacted: 83  |  Opted out: 29  |  Already closed: 41"],
      ],
      [3000, 6360]
    ),
    sp(40),

    h3("Propensity Scoring (Current)"),
    p("Propensity scores generated in gold_member_gap as uniform random (20.0-95.0). Channel routing: score > 75 = Call, > 40 = SMS, else Email."),
    sp(40),

    h2("2.2 ML Model Architecture (Production Design)"),
    p("Designed ML models to replace rule-based heuristics with data-driven predictions:"),
    sp(40),

    h3("Member Propensity Model"),
    bb("Algorithm", "XGBoost gradient-boosted classifier"),
    bb("Objective", "Predict gap closure probability per member-measure pair"),
    bb("Features", "Demographics, claims history (ICD-10 categories, frequency), pharmacy adherence (PDC), outreach response history, prior gap closure rate"),
    bb("Training Data", "silver_member + silver_claim + silver_pharmacy_fill + silver_outreach_event + gold_member_gap"),
    bb("Output", "Probability 0.0-1.0 replacing uniform random propensity"),
    bb("Refresh", "Weekly retrain on 90-day rolling window"),
    sp(40),

    h3("Closure Rate Predictor"),
    bb("Algorithm", "Random Forest regressor"),
    bb("Objective", "Per-member closure probability given channel, incentive, timing, and member features"),
    bb("Integration", "Replaces static CLOSURE_RATES dict in simulator_engine.py"),
    bb("Features", "Propensity score, channel preference, gap duration, measure weight, incentive sensitivity"),
    sp(40),

    h3("Star Rating Forecaster"),
    bb("Algorithm", "Prophet (seasonal decomposition) + ARIMA (short-term trend)"),
    bb("Objective", "Project end-of-year compliance rates with intervention lift and seasonal patterns"),
    bb("Output", "Projected rate with confidence intervals, replacing current random offset approach"),
    sp(40),

    h3("Member Churn Risk Model"),
    bb("Algorithm", "Logistic Regression (L2 regularized)"),
    bb("Objective", "Predict disenrollment probability within 90 days"),
    bb("Features", "Enrollment tenure, utilization trend, CAHPS sentiment, grievance history, product_type, dual_eligible_flag"),
    sp(40),

    h2("2.3 Feature Engineering"),
    tbl(
      ["Feature Group", "Source Tables", "Key Features"],
      [
        ["Demographic", "silver_member", "age, gender, state, product_type, dual_eligible, lis_flag, utilization_segment"],
        ["Clinical", "silver_claim", "claims_count_90d, unique_icd10_count, avg_paid_amount, chronic_condition_flag"],
        ["Pharmacy", "silver_pharmacy_fill", "pdc_ratio, avg_days_supply, drug_class_count, generic_rate, fill_frequency"],
        ["Behavioral", "silver_outreach_event", "total_contacts, response_rate, preferred_channel, opt_out_flag"],
        ["Call Center", "silver_call_event", "avg_sentiment, call_frequency, escalation_rate, avg_call_duration"],
        ["Gap History", "gold_member_gap", "gap_count, avg_days_open, prior_closure_rate, suppression_flag"],
      ],
      [1800, 3000, 4560]
    ),
    sp(80),

    h2("2.4 Model Registry & Lifecycle (MLflow)"),
    ...mono([
      "ML MODEL LIFECYCLE",
      "",
      "+----------+    +----------+    +----------+    +----------+    +----------+",
      "| Feature  | -> | Training | -> | MLflow   | -> | Model    | -> | Dashboard|",
      "| Store    |    | Pipeline |    | Registry |    | Serving  |    | API      |",
      "+----------+    +----------+    +----------+    +----------+    +----------+",
      "     ^                               |               |               |",
      "     |                          +---------+     +---------+     +---------+",
      "     +-- Retraining Trigger <-- | Monitor | <-- | Drift   | <-- | Feedback|",
      "                                +---------+     +---------+     +---------+",
    ]),
    sp(40),
    bullet("Experiment Tracking: MLflow with hyperparameter logging, AUC/precision/recall metrics"),
    bullet("Model Registry: Unity Catalog registry with staging/production promotion"),
    bullet("Model Serving: Databricks endpoints for real-time inference"),
    bullet("Monitoring: Data drift detection, prediction drift, automated retraining triggers"),
    bullet("A/B Testing: Canary deployment with traffic splitting between rules and ML"),
    pb(),
  ];
}

// ── SECTION 3: ANALYTICS & INTELLIGENCE LAYER ──────────────────────────────
function genaiSection() {
  return [
    h1("3. Analytics & Intelligence Layer"),

    h2("3.1 AI-Surfaced Features in UI"),
    p("The following platform features present algorithmic intelligence to end users:"),
    tbl(
      ["Feature", "UI Location", "Current Implementation"],
      [
        ["AI Copilot", "Agent Execution", "Static resolution scripts selected by call disposition type"],
        ["Alert Narratives", "Alerts & Priorities", "Template-driven alert text generated from scorecard metrics (current_rate, target_rate, open_gap_count)"],
        ["Intervention Recs", "CAHPS Interventions", "10 hardcoded intervention programs with expected lift percentages (1.5%-4.1%)"],
        ["Outreach Scripts", "Agent Execution", "Pre-built scripts with member context variables (name, measure, gap status)"],
        ["Campaign Suggestions", "Simulator", "Rule-based channel routing: propensity > 75 = Call, > 40 = SMS, else Email"],
      ],
      [2200, 2600, 4560]
    ),
    sp(80),

    h2("3.2 Sentiment & NLP Pipeline"),
    p("Current sentiment processing in the platform:"),
    tbl(
      ["Component", "Implementation", "Data Flow"],
      [
        ["CAHPS Survey", "Top-box flag: Likert >= 4 or Rating-10 >= 9", "bronze_cahps_survey_raw -> silver_cahps_response (top_box_flag computed)"],
        ["Call Center", "Synthetic sentiment_score (-1.0 to +1.0) per call", "bronze_call_center_raw -> silver_call_event (score passthrough)"],
        ["Composite Scoring", "6 composites (GNC, GCQ, DC, CS, HPR, CC) with top-box rates", "silver_cahps_response -> gold_cahps_overview (aggregated by plan)"],
        ["Department Mapping", "6 departments own specific composites", "gold_team_view: Clinical Quality, Member Experience, Call Center, Pharmacy, Utilization Mgmt, Network"],
      ],
      [1800, 3200, 4360]
    ),
    sp(40),

    h3("Sentiment Score Distribution by Disposition"),
    tbl(
      ["Call Disposition", "Sentiment Range", "Interpretation"],
      [
        ["Reached - Scheduled", "+0.1 to +1.0", "Positive (member agreed to action)"],
        ["Reached - Declined", "-0.5 to +0.2", "Mixed (member engaged but refused)"],
        ["Opted Out", "-1.0 to -0.2", "Negative (member requested no contact)"],
        ["No Answer / Voicemail", "-0.3 to +0.3", "Neutral (no interaction)"],
        ["Callback Requested", "+0.0 to +0.6", "Mildly positive (member interested)"],
      ],
      [2600, 2400, 4360]
    ),
    sp(40),

    h2("3.3 Alert Generation Engine"),
    p("gold_alert_priority rows are auto-generated from gold_measure_scorecard by applying threshold logic:"),
    bullet("Gap > 15 pts below target = critical severity"),
    bullet("Gap > 5 pts below target = warning severity"),
    bullet("Gap > 0 pts below target = info severity"),
    bullet("measure_status = red overrides to critical; yellow overrides to warning"),
    bullet("Priority score = abs(gap) * 10 + (30 if critical), capped at 99"),
    bullet("CTA routing: critical -> Simulator page, HEDIS -> HEDIS page, CAHPS -> CAHPS page"),
    sp(40),

    h2("3.4 Intervention Tracking"),
    p("10 named intervention programs tracked in gold_intervention_hub:"),
    tbl(
      ["Intervention", "Measure", "Department", "Expected Lift", "Status"],
      [
        ["COL Reminder Letter Campaign", "COL", "Clinical Quality", "+3.2%", "Active"],
        ["CBP PCP Alert Program", "CBP", "Network", "+2.8%", "Active"],
        ["KED Lab Order Nudge", "KED", "Clinical Quality", "+2.4%", "Planned"],
        ["AMM Care Management Referral", "AMM", "Care Management", "+4.1%", "Active"],
        ["OMW Fracture Risk Outreach", "OMW", "Clinical Quality", "+2.1%", "Planned"],
        ["SPC Statin Adherence Coaching", "SPC", "Pharmacy", "+1.8%", "Planned"],
        ["BCS Mobile Mammo Unit", "BCS", "Network", "+3.5%", "Planned"],
        ["HBD Diabetic Care Coordination", "HBD", "Clinical Quality", "+2.2%", "Active"],
        ["EED Eye Exam Transport", "EED", "Care Management", "+1.5%", "Planned"],
        ["TRC Transition Coach Program", "TRC", "Call Center", "+2.9%", "Active"],
      ],
      [2800, 1200, 1800, 1400, 2160]
    ),
    pb(),
  ];
}

// ── SECTION 4: PREDICTIVE INTELLIGENCE ──────────────────────────────────────
function predictiveSection() {
  return [
    h1("4. Predictive Intelligence"),

    h2("4.1 Gap Closure Prediction"),
    p("The simulator engine computes gap closure projections using a deterministic model:"),
    sp(20),
    ...mono([
      "SIMULATOR FORMULA:",
      "",
      "eligible_pool = total_gaps * gap_weight[status] * propensity_weight[tier]",
      "               - suppressions (contacted + opted_out + already_closed)",
      "",
      "closures[week] = eligible * closure_rate[channel] * (1 + incentive_boost)",
      "                 * waterfall[week]",
      "",
      "new_rate = current_rate + (total_closures / eligible_members * 100)",
      "new_star = rate_to_stars(new_rate, measure_thresholds)",
      "cost    = members_reached * cost_base[channel] + incentive_cost",
      "roi     = (star_improvement_value - total_cost) / total_cost",
    ]),
    sp(40),
    p("Production enhancement: Replace static closure_rate dict with per-member XGBoost predictions. Replace waterfall constants with time-series learned decay curves."),
    sp(40),

    h2("4.2 Star Rating Projection"),
    p("Current: projected_rate = current_rate + random offset (0.5-3.5 pts). Production: Prophet seasonal decomposition + ARIMA short-term trend with confidence intervals."),
    sp(40),

    h2("4.3 Risk Stratification"),
    p("Members segmented by utilization_segment (Low/Medium/High) based on claims frequency and paid amounts. HOS urgency scoring uses 7 weighted factors:"),
    tbl(
      ["Factor", "Weight", "Source"],
      [
        ["Survey completion likelihood", "20%", "silver_member (age, tenure)"],
        ["Physical health risk", "20%", "silver_claim (chronic conditions)"],
        ["Mental health risk", "15%", "silver_pharmacy_fill (antidepressant PDC)"],
        ["Gap count", "15%", "gold_member_gap (open gaps)"],
        ["Prior survey response", "10%", "silver_outreach_event (response rate)"],
        ["Dual/LIS status", "10%", "silver_member (dual_eligible, lis_flag)"],
        ["Recency of last contact", "10%", "silver_call_event (last call date)"],
      ],
      [3000, 1200, 5160]
    ),
    sp(40),

    h2("4.4 Campaign ROI Prediction"),
    p("180 historical campaigns in gold_campaign_performance provide training data for ROI prediction. Features: measure_code, channel, member_count, incentive_type, campaign_duration, baseline_rate. Enables pre-launch ROI estimation for campaign planning."),
    pb(),
  ];
}

// ── BUILD DOCUMENT ──────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 36, bold: true, font: "Arial" }, paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: "Arial" }, paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: "Arial" }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [{
      reference: "b",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    }]
  },
  sections: [{
    properties: {
      page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } },
    },
    headers: {
      default: new Header({ children: [
        new Paragraph({
          spacing: { after: 0 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: ORANGE } },
          children: [
            new TextRun({ text: "StarPulse  |  Architecture, ML & GenAI Reference", size: 18, font: "Arial", color: "999999" }),
          ],
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        })
      ] })
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({
          spacing: { after: 0 },
          border: { top: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" } },
          children: [
            new TextRun({ text: "EXL Services  |  Confidential", size: 16, font: "Arial", color: "999999" }),
            new TextRun({ text: "\t", size: 16, font: "Arial" }),
            new TextRun({ text: "Page ", size: 16, font: "Arial", color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: "999999" }),
          ],
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        })
      ] })
    },
    children: [
      ...cover(),
      ...archSection(),
      ...mlSection(),
      ...genaiSection(),
      ...predictiveSection(),
    ]
  }]
});

const OUT = "C:\\STARS_FInal_Draft\\StarPulse_Arch_ML_v2.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log("Generated:", OUT);
  console.log("File size:", Math.round(buf.length / 1024), "KB");
});
