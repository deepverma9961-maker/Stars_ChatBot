const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak, TabStopType, TabStopPosition,
  TableOfContents
} = require("docx");

// ── Constants ────────────────────────────────────────────────────────────────
const PAGE_W = 12240;
const PAGE_H = 15840;
const MARGIN = 1440;
const CONTENT_W = PAGE_W - 2 * MARGIN; // 9360

const BLUE = "1B3A5C";
const ORANGE = "F26722";
const LIGHT_BLUE = "D5E8F0";
const LIGHT_GRAY = "F2F2F2";
const MED_GRAY = "E8E8E8";
const WHITE = "FFFFFF";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorders = {
  top: { style: BorderStyle.NONE, size: 0 },
  bottom: { style: BorderStyle.NONE, size: 0 },
  left: { style: BorderStyle.NONE, size: 0 },
  right: { style: BorderStyle.NONE, size: 0 },
};
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

// ── Helpers ──────────────────────────────────────────────────────────────────
function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text, bold: true, size: 36, font: "Arial", color: BLUE })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text, bold: true, size: 28, font: "Arial", color: BLUE })] });
}
function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text, bold: true, size: 24, font: "Arial", color: "333333" })] });
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120, ...(opts.spacing || {}) },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, size: 22, font: "Arial", color: opts.color || "333333", bold: !!opts.bold, italics: !!opts.italics })]
  });
}
function pRuns(runs, opts = {}) {
  return new Paragraph({
    spacing: { after: 120, ...(opts.spacing || {}) },
    alignment: opts.align || AlignmentType.LEFT,
    children: runs.map(r => new TextRun({ size: 22, font: "Arial", color: "333333", ...r }))
  });
}
function bullet(text, ref = "bullets", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: "333333" })]
  });
}
function bulletBold(label, desc, ref = "bullets", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { after: 60 },
    children: [
      new TextRun({ text: label + ": ", size: 22, font: "Arial", color: "333333", bold: true }),
      new TextRun({ text: desc, size: 22, font: "Arial", color: "333333" })
    ]
  });
}
function monoBlock(lines) {
  return lines.map(line => new Paragraph({
    spacing: { after: 0, line: 260 },
    children: [new TextRun({ text: line, size: 18, font: "Courier New", color: "333333" })]
  }));
}
function spacer(pts = 120) {
  return new Paragraph({ spacing: { after: pts }, children: [] });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function makeRow(cells, opts = {}) {
  return new TableRow({
    children: cells.map((c, i) => new TableCell({
      borders,
      width: { size: c.w || 2000, type: WidthType.DXA },
      shading: { fill: opts.header ? BLUE : (opts.shading || WHITE), type: ShadingType.CLEAR },
      margins: cellMargins,
      verticalAlign: "center",
      children: [new Paragraph({
        spacing: { after: 0 },
        children: [new TextRun({
          text: c.t || "",
          size: opts.header ? 20 : 20,
          font: "Arial",
          bold: !!opts.header || !!c.bold,
          color: opts.header ? WHITE : "333333"
        })]
      })]
    }))
  });
}

function makeTable(headers, rows, colWidths) {
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      makeRow(headers.map((h, i) => ({ t: h, w: colWidths[i] })), { header: true }),
      ...rows.map((row, ri) =>
        makeRow(row.map((t, i) => ({ t, w: colWidths[i] })), { shading: ri % 2 === 0 ? LIGHT_GRAY : WHITE })
      )
    ]
  });
}

// ── COVER PAGE ───────────────────────────────────────────────────────────────
function coverPage() {
  return [
    spacer(600),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [new TextRun({ text: "EXL Services | StarPulse", size: 28, font: "Arial", color: ORANGE, bold: true })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "Medicare Stars Management Platform", size: 24, font: "Arial", color: "666666" })] }),
    spacer(200),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Technical Design Document", size: 52, font: "Arial", color: BLUE, bold: true })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "AI-Powered Stars Performance Intelligence", size: 28, font: "Arial", color: ORANGE })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: "for Medicare Advantage Health Plans", size: 24, font: "Arial", color: "666666" })] }),
    spacer(400),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: ORANGE } }, children: [] }),
    spacer(100),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Version 1.0  |  May 2026  |  Confidential", size: 22, font: "Arial", color: "888888" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Prepared by: EXL Health Analytics & AI Practice", size: 22, font: "Arial", color: "888888" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Platform: Databricks Lakehouse  |  Deployment: Databricks Apps (AWS)", size: 20, font: "Arial", color: "999999" })] }),
    spacer(300),
    makeTable(
      ["Property", "Value"],
      [
        ["Document ID", "TDD-STARPULSE-2026-001"],
        ["Classification", "Confidential - Internal Use"],
        ["Client", "EXL Services - Health Division"],
        ["Author", "StarPulse Engineering Team"],
        ["Approved By", "VP, Health Analytics & AI"],
        ["Live URL", "https://stars-pulse-1356475297832733.aws.databricksapps.com"],
        ["Databricks Workspace", "aiagenticdemo (Unity Catalog)"],
      ],
      [3000, 6360]
    ),
    pageBreak(),
  ];
}

// ── REVISION HISTORY ─────────────────────────────────────────────────────────
function revisionHistory() {
  return [
    h1("Revision History"),
    makeTable(
      ["Version", "Date", "Author", "Description"],
      [
        ["1.0", "2026-05-21", "StarPulse Engineering", "Initial TDD release - comprehensive platform documentation"],
        ["0.9", "2026-05-10", "StarPulse Engineering", "Draft review with architecture diagrams and data model"],
        ["0.8", "2026-04-28", "StarPulse Engineering", "Backend data model and pipeline documentation"],
        ["0.7", "2026-04-15", "StarPulse Engineering", "ML/GenAI architecture design sections"],
      ],
      [1200, 1800, 2800, 3560]
    ),
    pageBreak(),
  ];
}

// ── SECTION 1: EXECUTIVE SUMMARY ─────────────────────────────────────────────
function section1() {
  return [
    h1("1. Executive Summary"),

    h2("1.1 Platform Overview"),
    p("StarPulse is an enterprise-grade, AI-powered Medicare Stars management platform designed to help Medicare Advantage health plans optimize their CMS Star Ratings across all quality domains. The platform provides end-to-end visibility from portfolio-level KPIs to individual member gap closure, leveraging Databricks Lakehouse as the unified data and intelligence platform."),
    p("The system manages 14 health plan contracts across 14 states with a combined enrollment footprint of approximately 980,000 members. It tracks 45 quality measures spanning HEDIS clinical quality (14 measures), CAHPS member experience (8 composites), HOS health outcomes (5 measures), Part D medication adherence (5 measures), and operational metrics (13 measures). Each measure is weighted (1x or 3x) per CMS methodology, directly impacting overall star calculations and Quality Bonus Payment (QBP) eligibility."),

    h2("1.2 Business Drivers"),
    p("The platform addresses a critical business imperative: plans rated 4 stars or above receive QBP rebates from CMS, representing substantial revenue. Across the StarPulse portfolio:"),
    bullet("9 of 14 contracts currently at or above 4-star threshold (bonus-eligible)"),
    bullet("Estimated QBP at stake: $32.15M across the portfolio"),
    bullet("Highest single-plan exposure: $6.74M (H2213, Pacific Care Advantage Gold, CA)"),
    bullet("5 contracts at 3.0-3.5 stars require targeted intervention to reach bonus eligibility"),
    bullet("83-day measurement window countdown drives urgency for gap closure campaigns"),
    p("Every 0.5-star improvement for a non-bonus plan can unlock $2-4M in annual QBP revenue. StarPulse quantifies this opportunity at the measure level and orchestrates the outreach campaigns to capture it."),

    h2("1.3 Solution Scope"),
    p("StarPulse delivers a complete analytics and operations platform:"),
    bulletBold("14 Dashboard Pages", "Marketing Overview, Executive Summary, Plan Detail, HEDIS Measures, Campaign Simulator, Agent Execution, CAHPS (5 sub-tabs), HOS Measures, Impact Projector, Campaign History & ROI, Alerts & Priorities, Member 360, EHO4all Equity Dashboard, Market Analysis"),
    bulletBold("25+ Delta Lake Tables", "Organized across Bronze (5 raw), Silver (9 curated), Gold (12 analytic) layers in Databricks Unity Catalog"),
    bulletBold("18 REST API Endpoints", "FastAPI backend with Databricks SQL Warehouse connectivity and intelligent fallback"),
    bulletBold("14 Data Pipeline Notebooks", "Automated daily execution via Databricks Workflows (6:00 AM ET)"),
    bulletBold("Real-time Outreach", "Twilio SMS and SendGrid email integration for member gap closure campaigns"),
    bulletBold("Star Rating Simulator", "What-if scenario modeling with 4-week waterfall projections and segment-level ROI analysis"),

    h2("1.4 Key Differentiators"),
    bullet("Propensity-driven member targeting with channel and incentive optimization"),
    bullet("NLP-enriched CAHPS survey analysis with sentiment detection and real-time pulse monitoring"),
    bullet("AI agent copilot for call center resolution guidance during live member interactions"),
    bullet("EHO4all equity dashboard tracking LIS/Dual subgroup disparity gaps (CMS 2027 CAI replacement)"),
    bullet("Closed-loop outreach: simulate, execute, measure ROI within a single platform"),
    bullet("Market intelligence module with competitive benchmarking across CMS public datasets"),
    pageBreak(),
  ];
}

// ── SECTION 2: OVERALL SOLUTION ARCHITECTURE ─────────────────────────────────
function section2() {
  return [
    h1("2. Overall Solution Architecture"),

    h2("2.1 Architecture Principles"),
    p("The StarPulse platform is built on the following architectural principles:"),
    bulletBold("Medallion Lakehouse", "Three-tier data organization (Bronze/Silver/Gold) ensuring data lineage, auditability, and progressive refinement from raw ingestion to analytics-ready aggregates"),
    bulletBold("API-First Design", "All data access is mediated through a RESTful API layer, decoupling the frontend from direct database access and enabling multi-client consumption"),
    bulletBold("Fail-Safe Fallback", "Every API endpoint implements graceful degradation with in-memory fallback data, ensuring zero-downtime user experience even during Databricks connectivity interruptions"),
    bulletBold("Unity Catalog Governance", "All tables are managed through Databricks Unity Catalog, providing centralized access control, data lineage, and audit logging"),
    bulletBold("Synthetic-Data Safe", "The platform uses HIPAA-safe synthetic data with deterministic seeding for reproducibility, enabling full-fidelity demonstrations without PHI exposure"),

    h2("2.2 End-to-End Data Flow"),
    p("The complete data flow from source systems to dashboard visualization follows this path:"),
    spacer(40),
    ...monoBlock([
      "+------------------+     +------------------+     +------------------+",
      "| Source Systems   |     | Databricks       |     | Application      |",
      "| (Claims, Rx,     | --> | Lakehouse        | --> | Layer            |",
      "|  Surveys, Calls) |     | (Medallion)      |     | (FastAPI + SPA)  |",
      "+------------------+     +------------------+     +------------------+",
      "                                 |                        |",
      "   +-------------+     +---------+---------+     +--------+--------+",
      "   | Bronze      |     | Silver            |     | Gold            |",
      "   | 5 raw tbls  |     | 9 curated tbls    |     | 12 analytic tbls|",
      "   | 3.3M rows   |     | 3.5M+ rows        |     | ~280K rows      |",
      "   +-------------+     +-------------------+     +-----------------+",
      "                                                         |",
      "   +-------------------+     +-----------------+     +---+------------+",
      "   | SQL Warehouse     | <-- | FastAPI REST    | --> | React SPA      |",
      "   | (Serverless)      |     | 13 routers      |     | 14 pages       |",
      "   +-------------------+     | 18 endpoints    |     | Chart.js       |",
      "                             +-----------------+     +----------------+",
      "                                     |",
      "                             +-------+-------+",
      "                             | Twilio  | SendGrid |",
      "                             | (SMS)   | (Email)  |",
      "                             +---------+----------+",
    ]),
    spacer(80),

    h2("2.3 Technology Stack"),
    makeTable(
      ["Layer", "Technology", "Version / Details"],
      [
        ["Compute Runtime", "Databricks Runtime", "14.3.x-scala2.12 (Spark 3.5.0)"],
        ["Storage", "Delta Lake", "Unity Catalog managed tables, ACID transactions"],
        ["Catalog", "Unity Catalog", "aiagenticdemo catalog, 3 schemas (stars_bronze/stars_silver/stars_gold)"],
        ["SQL Engine", "Databricks SQL Warehouse", "Serverless, auto-scaling, Photon-accelerated"],
        ["Orchestration", "Databricks Workflows", "Daily 6:00 AM ET, 14-task DAG, auto-retry"],
        ["API Framework", "FastAPI", "0.111.0 with Pydantic v2 validation"],
        ["API Runtime", "Uvicorn", "0.29.0 (ASGI, async workers)"],
        ["DB Connector", "databricks-sql-connector", "3.4.0 (ODBC/Thrift)"],
        ["Frontend", "React 18 + Vite", "SPA with TanStack Query, Recharts, Chart.js 4.4"],
        ["SMS Outreach", "Twilio REST API", "v9.0.5 Python SDK"],
        ["Email Outreach", "SendGrid v3 API", "v6.11.0 Python SDK"],
        ["Deployment", "Databricks Apps", "Serverless, AWS-hosted, auto-TLS"],
        ["Data Generation", "Faker + NumPy", "Deterministic synthetic data (seed=42)"],
      ],
      [2200, 2800, 4360]
    ),
    spacer(80),

    h2("2.4 Catalog & Schema Organization"),
    p("All platform data resides in the aiagenticdemo Unity Catalog with the following schema structure:"),
    makeTable(
      ["Schema", "Purpose", "Table Count", "Total Rows"],
      [
        ["stars_bronze", "Raw ingestion layer - source fidelity preserved (includes CMS reference lookups)", "5+", "~3.3M"],
        ["stars_silver", "Curated layer - PII hashed, typed, enriched", "9", "~3.5M"],
        ["stars_gold", "Analytics layer - pre-aggregated, dashboard-ready (includes CMS market reference)", "15", "~282K"],
      ],
      [1500, 4000, 1600, 2260]
    ),
    spacer(80),

    h2("2.5 API Architecture"),
    p("The FastAPI backend exposes 18 endpoints across 13 routers, all prefixed under /api. Each router follows a consistent pattern: attempt Databricks SQL query, catch exceptions, return in-memory fallback data with a degradation flag."),
    makeTable(
      ["Router", "Key Endpoints", "Backing Gold Tables"],
      [
        ["star_summary", "GET /api/star-summary", "gold_star_rating_summary"],
        ["plans", "GET /api/plans, /api/plans/{id}", "gold_star_rating_summary + silver_plan"],
        ["hedis", "GET /api/hedis-measures", "gold_measure_scorecard + silver_measure"],
        ["cahps", "GET /api/cahps, /api/cahps/pulse", "gold_cahps_overview + silver_cahps_response"],
        ["members", "GET /api/members/gaps, /api/members/{key}", "gold_member_gap + silver_member"],
        ["campaigns", "GET /api/campaigns", "gold_campaign_performance"],
        ["alerts", "GET /api/alerts", "gold_alert_priority"],
        ["interventions", "GET /api/interventions", "gold_intervention_hub"],
        ["team_view", "GET /api/team-view", "gold_team_view"],
        ["simulator", "POST /api/simulator/run", "gold_measure_scorecard (context)"],
        ["hos", "GET /api/hos/measures, /members, /providers, /summary", "gold_hos_* (4 tables)"],
        ["market", "GET /api/market/enrollment, /plan-stars, /measure-stars", "stars_gold.cms_* (3 tables)"],
        ["outreach", "POST /api/outreach/send-bundle", "N/A (Twilio/SendGrid)"],
      ],
      [1800, 3800, 3760]
    ),
    spacer(80),

    h2("2.6 Deployment Topology"),
    p("StarPulse is deployed as a Databricks App, which provides a fully managed serverless hosting environment:"),
    bullet("Application entry point: uvicorn backend.main:app --host 0.0.0.0 --port 8000"),
    bullet("Frontend: Compiled React SPA served as static files from /frontend/dist/index.html"),
    bullet("SPA routing: All non-API routes return index.html (client-side routing)"),
    bullet("Health monitoring: GET /api/health (liveness) and GET /api/connection-status (Databricks connectivity)"),
    bullet("Live URL: https://stars-pulse-1356475297832733.aws.databricksapps.com"),
    bullet("CORS: Configured for Databricks Apps domain; all origins allowed in development"),
    pageBreak(),
  ];
}

// ── SECTION 3: DATA MODEL ────────────────────────────────────────────────────
function section3() {
  const content = [
    h1("3. Databricks Backend Design - Data Model"),

    h2("3.1 Data Model Design Philosophy"),
    p("The StarPulse data model implements the Databricks Medallion Architecture with three progressive refinement layers. Each layer adds value through transformation, enrichment, and aggregation:"),
    bulletBold("Bronze (Raw)", "Source-faithful ingestion with minimal transformation. Preserves all original fields plus audit metadata (raw_source, ingestion_ts). Enables replay and reprocessing from any point in time."),
    bulletBold("Silver (Curated)", "Cleansed, typed, and enriched data. PII fields are SHA-256 hashed. Surrogate keys (UUID-based member_key, plan_key, measure_key, provider_key) replace natural keys to decouple from source systems. Partitioned by temporal dimensions for query performance."),
    bulletBold("Gold (Analytics)", "Pre-aggregated, dashboard-ready tables. One row per analytical entity (plan, member-gap, campaign). Status flags computed from business thresholds. Directly consumed by FastAPI endpoints with no further transformation needed."),
    spacer(40),

    h2("3.2 Bronze Layer Tables"),
    p("The Bronze layer contains 5 tables with a combined volume of approximately 3.3 million rows. All tables are stored as Delta Lake managed tables with full ACID transaction support.", { italics: true }),
    spacer(40),

    h3("3.2.1 bronze_enrollment_raw"),
    p("Member enrollment records with demographics and plan assignment. 100,000 rows."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["member_id", "STRING", "No (PK)", "Unique member identifier (MBR-0000000)"],
        ["synthetic_mbi", "STRING", "Yes", "Medicare Beneficiary Identifier (synthetic)"],
        ["first_name", "STRING", "Yes", "Member first name"],
        ["last_name", "STRING", "Yes", "Member last name"],
        ["date_of_birth", "STRING", "Yes", "DOB as YYYY-MM-DD string"],
        ["gender", "STRING", "Yes", "M or F"],
        ["state", "STRING", "Yes", "Two-letter state code"],
        ["contract_id", "STRING", "Yes", "CMS contract identifier (H3312, H5521, etc.)"],
        ["product_type", "STRING", "Yes", "HMO, PPO, D-SNP, or HMO-POS"],
        ["dual_eligible_flag", "BOOLEAN", "Yes", "Medicare/Medicaid dual-eligible (20% rate)"],
        ["lis_flag", "BOOLEAN", "Yes", "Low Income Subsidy flag (30% rate)"],
        ["effective_date", "STRING", "Yes", "Enrollment effective date"],
        ["termination_date", "STRING", "Yes", "Termination date (null if active)"],
        ["raw_source", "STRING", "Yes", "Source system identifier"],
        ["ingestion_ts", "STRING", "Yes", "Ingestion timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.2.2 bronze_claims_raw"),
    p("Medical claims with diagnosis codes, procedures, and paid amounts. 1.8 million rows across 4 utilization tiers: Low (35K members, 8 avg claims), Moderate (40K, 18), Chronic (20K, 28), High Risk (5K, 40)."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["claim_id", "STRING", "No (PK)", "Unique claim identifier (CLM-000000000)"],
        ["member_id", "STRING", "Yes (FK)", "References bronze_enrollment_raw.member_id"],
        ["utilization_tier", "STRING", "Yes", "Low, Moderate, Chronic, HighRisk"],
        ["service_date", "STRING", "Yes", "Date of service (YYYY-MM-DD)"],
        ["icd10_primary", "STRING", "Yes", "Primary ICD-10 diagnosis (E11.9, I10, etc.)"],
        ["icd10_secondary", "STRING", "Yes", "Secondary diagnosis (null 40% of time)"],
        ["cpt_code", "STRING", "Yes", "Procedure code (G0438, 83036, 77067, etc.)"],
        ["revenue_code", "STRING", "Yes", "Revenue center code"],
        ["rendering_npi", "STRING", "Yes", "Rendering provider NPI"],
        ["facility_npi", "STRING", "Yes", "Facility NPI (null 50% of time)"],
        ["claim_type", "STRING", "Yes", "Professional, Facility, or Ancillary"],
        ["plan_paid_amount", "DOUBLE", "Yes", "Plan paid amount ($15-$850)"],
        ["member_paid_amount", "DOUBLE", "Yes", "Member cost share ($0-$45)"],
        ["raw_source", "STRING", "Yes", "Source system identifier"],
        ["ingestion_ts", "STRING", "Yes", "Ingestion timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.2.3 bronze_pharmacy_raw"),
    p("Prescription drug fill records mapped to HEDIS quality measures. 1.1 million rows. Drug classes include: statins (SPC measure), antidepressants (AMM), antihypertensives (CBP), diabetes medications (HBD/KED), and osteoporosis drugs (OMW)."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["rx_id", "STRING", "No (PK)", "Unique prescription ID (RX-000000000)"],
        ["member_id", "STRING", "Yes (FK)", "References bronze_enrollment_raw"],
        ["fill_date", "STRING", "Yes", "Fill date (YYYY-MM-DD)"],
        ["ndc_code", "STRING", "Yes", "11-digit National Drug Code"],
        ["drug_name", "STRING", "Yes", "Drug name with strength"],
        ["drug_class", "STRING", "Yes", "statin, antidepressant, antihypertensive, diabetes, osteoporosis"],
        ["days_supply", "INT", "Yes", "30 or 90 day supply"],
        ["quantity", "INT", "Yes", "Quantity dispensed"],
        ["pharmacy_npi", "STRING", "Yes", "Dispensing pharmacy NPI"],
        ["plan_paid_amount", "DOUBLE", "Yes", "Plan paid ($2.50-$180)"],
        ["member_paid_amount", "DOUBLE", "Yes", "Member copay ($0-$15)"],
        ["generic_flag", "BOOLEAN", "Yes", "Generic vs brand (70% generic rate)"],
        ["raw_source", "STRING", "Yes", "Source system identifier"],
        ["ingestion_ts", "STRING", "Yes", "Ingestion timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.2.4 bronze_cahps_survey_raw"),
    p("CAHPS survey responses across 6 composites with 13 questions total. 10,000 respondents from ~83,000 eligible members (12% sampling rate per CMS methodology). Scale types: Likert (1-4: Never/Sometimes/Usually/Always) and Rating-10 (0-10 health plan rating)."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["response_id", "STRING", "No (PK)", "Unique response ID"],
        ["member_id", "STRING", "Yes (FK)", "Respondent member ID"],
        ["survey_date", "STRING", "Yes", "Survey completion date"],
        ["composite_code", "STRING", "Yes", "GNC, GCQ, DC, CS, HPR, CC"],
        ["composite_name", "STRING", "Yes", "Full composite name"],
        ["question_code", "STRING", "Yes", "Individual question ID"],
        ["response_value", "INT", "Yes", "Likert 1-4 or Rating 0-10"],
        ["scale_type", "STRING", "Yes", "likert or rating_10"],
        ["raw_source", "STRING", "Yes", "Source system identifier"],
        ["ingestion_ts", "STRING", "Yes", "Ingestion timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.2.5 bronze_call_center_raw"),
    p("Call center interaction records with sentiment scoring. 375,000 calls across 6 queues (HEDIS_Outreach, CAHPS_Survey, Member_Services, Pharmacy_Support, Appeals, General) handled by 120 agents."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["call_id", "STRING", "No (PK)", "Unique call ID (CALL-00000000)"],
        ["member_id", "STRING", "Yes (FK)", "Member who was called/called in"],
        ["call_date", "STRING", "Yes", "Call date"],
        ["call_type", "STRING", "Yes", "inbound (40%) or outbound (60%)"],
        ["call_duration_min", "DOUBLE", "Yes", "Duration in minutes (0 for no-answer)"],
        ["disposition", "STRING", "Yes", "Reached-Scheduled, No Answer, Voicemail, etc."],
        ["sentiment_score", "DOUBLE", "Yes", "NLP sentiment (-1.0 to +1.0)"],
        ["agent_id", "STRING", "Yes", "Agent identifier (AGT-0001 to AGT-0120)"],
        ["queue_name", "STRING", "Yes", "Call queue assignment"],
        ["measure_code", "STRING", "Yes", "Related HEDIS measure (nullable)"],
        ["raw_source", "STRING", "Yes", "Source system identifier"],
        ["ingestion_ts", "STRING", "Yes", "Ingestion timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(40),

    h2("3.3 Silver Layer Tables"),
    p("The Silver layer transforms raw data into analytics-ready dimensions and facts. Key transformations include PII hashing (SHA-256), surrogate key assignment (UUID), type casting, and enrichment.", { italics: true }),
    spacer(40),

    h3("3.3.1 silver_member"),
    p("Curated member dimension with PII protection. 100,000 rows. All identifying information (MBI, phone, email) is SHA-256 hashed. Display name shows only first name + last initial."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["member_key", "STRING", "No (PK)", "UUID surrogate key"],
        ["member_id", "STRING", "Yes", "Original member ID"],
        ["display_name", "STRING", "Yes", "First name + last initial (e.g., John S.)"],
        ["member_mbi_hash", "STRING", "Yes", "SHA-256 hash of synthetic MBI"],
        ["phone_hash", "STRING", "Yes", "SHA-256 hash of phone"],
        ["email_hash", "STRING", "Yes", "SHA-256 hash of email"],
        ["age", "INT", "Yes", "Calculated age (2025 - birth year)"],
        ["gender", "STRING", "Yes", "M or F"],
        ["state", "STRING", "Yes", "State code"],
        ["contract_id", "STRING", "Yes", "CMS contract ID"],
        ["product_type", "STRING", "Yes", "Plan product type"],
        ["dual_eligible_flag", "BOOLEAN", "Yes", "Dual eligibility status"],
        ["lis_flag", "BOOLEAN", "Yes", "Low Income Subsidy status"],
        ["utilization_segment", "STRING", "Yes", "Low (35%), Moderate (40%), Chronic (20%), Very High Risk (5%)"],
        ["pcp_provider_key", "STRING", "Yes (FK)", "UUID FK to silver_provider"],
        ["effective_date", "STRING", "Yes", "Enrollment effective date"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.3.2 silver_plan"),
    p("Plan/contract dimension. 28 rows (14 base contracts + 14 D-SNP variants across FL, TX, CA, PA, NY, OH, AZ, GA, IL, NC, MI, WA, VA, CO)."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["plan_key", "STRING", "No (PK)", "Surrogate key (PLN-0000 to PLN-0027)"],
        ["contract_id", "STRING", "Yes", "CMS contract ID (H3312, H3312B, etc.)"],
        ["plan_name", "STRING", "Yes", "Full plan name"],
        ["state", "STRING", "Yes", "State of operation"],
        ["enrollment_count", "INT", "Yes", "Total enrolled members"],
        ["product_type", "STRING", "Yes", "HMO, PPO, D-SNP, HMO-POS"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.3.3 silver_provider"),
    p("Provider dimension with network tiering. 12,000 rows across 9 specialties and 3 network tiers."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["provider_key", "STRING", "No (PK)", "Surrogate key (PRV-000000)"],
        ["npi", "STRING", "Yes", "10-digit National Provider Identifier"],
        ["provider_name", "STRING", "Yes", "Provider name with title"],
        ["specialty", "STRING", "Yes", "Internal Medicine, Cardiology, etc. (9 types)"],
        ["network_tier", "STRING", "Yes", "Tier 1 Preferred (60%), Tier 2 In-Network (30%), Tier 3 Out (10%)"],
        ["tin_hash", "STRING", "Yes", "Hashed Tax ID Number"],
        ["state", "STRING", "Yes", "Practice state"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.3.4 silver_measure"),
    p("Complete quality measure catalog. 45 rows covering all CMS Star Rating domains."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["measure_key", "STRING", "No (PK)", "Surrogate key (MSR-0000)"],
        ["measure_code", "STRING", "Yes", "Short code (HBD, CBP, COL, GNC, etc.)"],
        ["measure_name", "STRING", "Yes", "Full CMS measure name"],
        ["measure_category", "STRING", "Yes", "HEDIS, CAHPS, HOS, PARTD, OPS"],
        ["part", "STRING", "Yes", "C (Part C) or D (Part D)"],
        ["measure_weight", "INT", "Yes", "CMS weight: 1x, 2x, or 3x"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.3.5 silver_cahps_response"),
    p("Processed CAHPS survey responses with top-box flag computation. ~120,000 rows (10K respondents x ~12 questions each). Top-box logic: Likert >= 4 (Always) OR Rating-10 >= 9."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["cahps_response_key", "STRING", "No (PK)", "UUID surrogate key"],
        ["member_id", "STRING", "Yes", "Respondent member"],
        ["survey_date", "STRING", "Yes", "Response date"],
        ["composite_code", "STRING", "Yes", "CAHPS composite code"],
        ["composite_name", "STRING", "Yes", "Full composite name"],
        ["question_code", "STRING", "Yes", "Individual question ID"],
        ["response_value", "INT", "Yes", "Response value"],
        ["scale_type", "STRING", "Yes", "likert or rating_10"],
        ["top_box_flag", "BOOLEAN", "Yes", "True if top-box response"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.3.6 silver_claim"),
    p("Curated claims joined to member dimension. ~1.8M rows. Partitioned by service_month for query performance."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["claim_key", "STRING", "No (PK)", "UUID surrogate key"],
        ["claim_id", "STRING", "Yes", "Original claim ID"],
        ["member_key", "STRING", "Yes (FK)", "FK to silver_member"],
        ["member_id", "STRING", "Yes", "Original member ID"],
        ["service_date", "STRING", "Yes", "Service date"],
        ["service_month", "DATE", "Yes", "Truncated to month (partition key)"],
        ["icd10_primary", "STRING", "Yes", "Primary diagnosis code"],
        ["icd10_secondary", "STRING", "Yes", "Secondary diagnosis code"],
        ["cpt_code", "STRING", "Yes", "Procedure code"],
        ["claim_type", "STRING", "Yes", "Claim type"],
        ["plan_paid_amount", "DOUBLE", "Yes", "Plan paid amount"],
        ["member_paid_amount", "DOUBLE", "Yes", "Member cost share"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    p("Partition strategy: PARTITION BY (service_month) - enables month-level pruning for temporal queries."),
    spacer(80),

    h3("3.3.7 silver_pharmacy_fill"),
    p("Curated pharmacy data with PDC compliance flag. ~1.1M rows. Partitioned by fill_month."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["rx_key", "STRING", "No (PK)", "UUID surrogate key"],
        ["rx_id", "STRING", "Yes", "Original Rx ID"],
        ["member_key", "STRING", "Yes (FK)", "FK to silver_member"],
        ["member_id", "STRING", "Yes", "Original member ID"],
        ["fill_date", "STRING", "Yes", "Fill date"],
        ["fill_month", "DATE", "Yes", "Truncated to month (partition key)"],
        ["ndc_code", "STRING", "Yes", "NDC drug code"],
        ["drug_name", "STRING", "Yes", "Drug name"],
        ["drug_class", "STRING", "Yes", "Therapeutic class"],
        ["days_supply", "INT", "Yes", "Days supply"],
        ["quantity", "INT", "Yes", "Quantity dispensed"],
        ["plan_paid_amount", "DOUBLE", "Yes", "Plan paid"],
        ["member_paid_amount", "DOUBLE", "Yes", "Member paid"],
        ["generic_flag", "BOOLEAN", "Yes", "Generic indicator"],
        ["pdc_compliant", "BOOLEAN", "Yes", "PDC >= 80% or probabilistic flag"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.3.8 silver_outreach_event"),
    p("Member outreach history across all channels. ~120,000 rows generated from 60,000 sampled members with 0-5 events each."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["outreach_key", "STRING", "No (PK)", "Surrogate key (OUT-000000000)"],
        ["member_key", "STRING", "Yes (FK)", "FK to silver_member"],
        ["member_id", "STRING", "Yes", "Original member ID"],
        ["outreach_date", "STRING", "Yes", "Date of outreach attempt"],
        ["channel", "STRING", "Yes", "Call, SMS, Email, Portal"],
        ["measure_code", "STRING", "Yes", "Target HEDIS measure"],
        ["response_status", "STRING", "Yes", "Reached-Scheduled (20%), No Answer (35%), Voicemail (20%), Opted Out (5%), Gap Closed (20%)"],
        ["agent_id", "STRING", "Yes", "Outreach agent"],
        ["campaign_name", "STRING", "Yes", "Linked campaign (nullable)"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.3.9 silver_call_event"),
    p("Curated call center events joined to member dimension. ~375,000 rows."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["call_event_key", "STRING", "No (PK)", "UUID surrogate key"],
        ["call_id", "STRING", "Yes", "Original call ID"],
        ["member_key", "STRING", "Yes (FK)", "FK to silver_member"],
        ["member_id", "STRING", "Yes", "Original member ID"],
        ["call_date", "STRING", "Yes", "Call date"],
        ["call_type", "STRING", "Yes", "inbound or outbound"],
        ["call_duration_min", "DOUBLE", "Yes", "Call duration"],
        ["disposition", "STRING", "Yes", "Call disposition"],
        ["sentiment_score", "DOUBLE", "Yes", "NLP sentiment score (-1.0 to +1.0)"],
        ["agent_id", "STRING", "Yes", "Agent identifier"],
        ["queue_name", "STRING", "Yes", "Queue assignment"],
        ["measure_code", "STRING", "Yes", "Related HEDIS measure"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(40),

    h2("3.4 Gold Layer Tables"),
    p("The Gold layer provides pre-aggregated, dashboard-ready tables. Each table maps directly to one or more UI pages, eliminating the need for complex joins at query time.", { italics: true }),
    spacer(40),

    h3("3.4.1 gold_star_rating_summary"),
    p("Portfolio-level star ratings. 14 rows (one per non-SNP contract). Feeds: Executive Overview, Plan Detail pages."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["star_summary_key", "STRING", "No (PK)", "Composite key (SS-{contract}-{year})"],
        ["plan_key", "STRING", "Yes (FK)", "FK to silver_plan"],
        ["contract_id", "STRING", "Yes", "CMS contract ID"],
        ["measurement_year", "INT", "Yes", "Measurement year (2025)"],
        ["prior_year_star_rating", "DOUBLE", "Yes", "Prior year overall stars"],
        ["projected_star_rating", "DOUBLE", "Yes", "Current projected stars"],
        ["hedis_domain_rating", "DOUBLE", "Yes", "HEDIS domain rating"],
        ["cahps_domain_rating", "DOUBLE", "Yes", "CAHPS domain rating"],
        ["hos_domain_rating", "DOUBLE", "Yes", "HOS domain rating"],
        ["partd_domain_rating", "DOUBLE", "Yes", "Part D domain rating"],
        ["bonus_eligible_flag", "BOOLEAN", "Yes", "True if projected >= 4.0"],
        ["estimated_bonus_amount", "DOUBLE", "Yes", "QBP estimate in dollars"],
        ["last_updated", "STRING", "Yes", "Last refresh timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.2 gold_measure_scorecard"),
    p("Measure-level performance scorecard. 1,260 rows (28 plans x 45 measures). H3312 values serve as reference baseline matching the frontend exactly. Feeds: HEDIS Measures, Plan Detail pages."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["scorecard_key", "STRING", "No (PK)", "Composite key (SC-{contract}-{measure}-{year})"],
        ["plan_key", "STRING", "Yes (FK)", "FK to silver_plan"],
        ["measure_key", "STRING", "Yes (FK)", "FK to silver_measure"],
        ["measurement_year", "INT", "Yes", "2025"],
        ["current_rate", "DOUBLE", "Yes", "Current compliance rate (%)"],
        ["open_gap_count", "LONG", "Yes", "Number of open care gaps"],
        ["measure_status", "STRING", "Yes", "green (>= 4-star+5), yellow (>= 4-star-8), red (< 4-star-8)"],
        ["target_rate", "DOUBLE", "Yes", "4-star threshold rate"],
        ["projected_rate", "DOUBLE", "Yes", "Projected end-of-year rate"],
        ["last_updated", "STRING", "Yes", "Last refresh timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.3 gold_member_gap"),
    p("Member-measure gap registry with propensity scoring and channel recommendations. ~260,000 rows. Core table for Simulator, Agent Execution, and Member 360 pages. Gap distribution: Open 55%, Partial 30%, Borderline 15%."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["member_gap_key", "STRING", "No (PK)", "Surrogate key (GAP-000000000)"],
        ["member_key", "STRING", "Yes (FK)", "FK to silver_member"],
        ["plan_key", "STRING", "Yes (FK)", "FK to silver_plan"],
        ["measure_key", "STRING", "Yes (FK)", "FK to silver_measure"],
        ["measure_code", "STRING", "Yes", "HEDIS measure code"],
        ["measurement_year", "INT", "Yes", "2025"],
        ["gap_status", "STRING", "Yes", "Open, Partial, or Borderline"],
        ["propensity_score", "DOUBLE", "Yes", "Closure propensity (20.0 - 95.0)"],
        ["recommended_channel", "STRING", "Yes", ">75: Call, >40: SMS, else: Email"],
        ["recommended_incentive", "STRING", "Yes", ">80: None, >60: $25, else: $50"],
        ["gap_open_date", "STRING", "Yes", "Date gap was identified"],
        ["last_outreach_date", "STRING", "Yes", "Most recent outreach (from silver_outreach_event)"],
        ["campaign_name", "STRING", "Yes", "Linked campaign (nullable)"],
        ["is_suppressed", "BOOLEAN", "Yes", "Suppression flag (10% rate)"],
        ["days_open", "INT", "Yes", "Days since gap opened (15-280)"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.4 gold_cahps_overview"),
    p("Plan-level CAHPS ratings and QBP exposure. 14 rows. Feeds: CAHPS Overview page."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["cahps_key", "STRING", "No (PK)", "Composite key"],
        ["plan_key", "STRING", "Yes (FK)", "FK to silver_plan"],
        ["contract_id", "STRING", "Yes", "CMS contract ID"],
        ["measurement_year", "INT", "Yes", "2025"],
        ["current_cahps_rating", "DOUBLE", "Yes", "Current overall CAHPS rating"],
        ["projected_cahps_rating", "DOUBLE", "Yes", "Projected CAHPS rating"],
        ["gap_to_4_star", "DOUBLE", "Yes", "Points needed to reach 4.0"],
        ["days_remaining", "INT", "Yes", "Days until measurement snapshot"],
        ["qbp_at_stake_amount", "DOUBLE", "Yes", "Quality Bonus Payment at risk ($)"],
        ["last_updated", "STRING", "Yes", "Last refresh timestamp"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.5 gold_team_view"),
    p("Department-level measure ownership and accountability. 6 rows. Feeds: Team View tab in CAHPS module."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["team_view_key", "STRING", "No (PK)", "Composite key"],
        ["department", "STRING", "Yes", "Clinical Quality, Member Experience, Call Center, Pharmacy, Utilization Mgmt, Network"],
        ["team_leader", "STRING", "Yes", "Department leader name"],
        ["measures_owned", "ARRAY<STRING>", "Yes", "List of owned measure codes"],
        ["measurement_year", "INT", "Yes", "2025"],
        ["on_track_count", "INT", "Yes", "Measures meeting target"],
        ["at_risk_count", "INT", "Yes", "Measures within 5pts of target"],
        ["critical_count", "INT", "Yes", "Measures >5pts below target"],
        ["action_status", "STRING", "Yes", "In Progress or Not Started"],
        ["next_action", "STRING", "Yes", "Next scheduled action description"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.6 gold_campaign_performance"),
    p("Campaign execution history with ROI metrics. 180 rows (7 seed campaigns + 173 historical). Feeds: Campaign History & ROI page."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["campaign_key", "STRING", "No (PK)", "UUID"],
        ["campaign_name", "STRING", "Yes", "Campaign name"],
        ["measure_code", "STRING", "Yes", "Target HEDIS measure"],
        ["primary_channel", "STRING", "Yes", "Call, SMS, or Email"],
        ["member_count", "LONG", "Yes", "Members targeted"],
        ["projected_closures", "LONG", "Yes", "Expected closures"],
        ["actual_closures", "LONG", "Yes", "Actual closures (null if active)"],
        ["lift_pct", "DOUBLE", "Yes", "Rate lift percentage"],
        ["total_cost", "DOUBLE", "Yes", "Total campaign cost ($)"],
        ["roi_multiplier", "DOUBLE", "Yes", "ROI factor (null if active)"],
        ["campaign_status", "STRING", "Yes", "Active or Completed"],
        ["campaign_start_date", "STRING", "Yes", "Start date"],
        ["campaign_end_date", "STRING", "Yes", "End date (null if active)"],
        ["measurement_year", "INT", "Yes", "2025"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.7 gold_alert_priority"),
    p("Auto-generated alerts from measure scorecard analysis. ~20 rows. Severity derived from gap-to-target distance and measure status. Feeds: Alerts & Priorities page."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["alert_id", "STRING", "No (PK)", "Alert identifier"],
        ["severity", "STRING", "Yes", "critical, warning, or info"],
        ["alert_title", "STRING", "Yes", "Alert headline"],
        ["alert_body", "STRING", "Yes", "Detailed alert text with metrics"],
        ["alert_meta", "STRING", "Yes", "Gap count or time-based context"],
        ["measure_code", "STRING", "Yes", "Related measure (nullable)"],
        ["cta_label", "STRING", "Yes", "Call-to-action button text"],
        ["cta_page", "STRING", "Yes", "Target page (simulator, hedis, cahps)"],
        ["priority_score", "INT", "Yes", "0-99 priority ranking"],
        ["is_active", "BOOLEAN", "Yes", "Alert active status"],
        ["measurement_year", "INT", "Yes", "2025"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.8 gold_intervention_hub"),
    p("Named intervention programs with lift projections. 10 rows across 5 departments. Feeds: CAHPS Interventions tab."),
    makeTable(
      ["Column", "Type", "Nullable", "Description"],
      [
        ["intervention_id", "STRING", "No (PK)", "Intervention identifier"],
        ["intervention_name", "STRING", "Yes", "Program name"],
        ["measure_key", "STRING", "Yes (FK)", "FK to silver_measure"],
        ["measure_code", "STRING", "Yes", "Target measure code"],
        ["owner_department", "STRING", "Yes", "Responsible department"],
        ["expected_lift_pct", "DOUBLE", "Yes", "Expected rate improvement (1.5% - 4.1%)"],
        ["intervention_status", "STRING", "Yes", "Active or Planned"],
        ["due_date", "STRING", "Yes", "Target completion date"],
        ["target_member_count", "LONG", "Yes", "Members in scope"],
        ["measurement_year", "INT", "Yes", "2025"],
      ],
      [2400, 1200, 1400, 4360]
    ),
    spacer(80),

    h3("3.4.9 - 3.4.12 HOS Gold Tables"),
    p("Four tables support the Health Outcomes Survey module:"),
    bulletBold("gold_hos_measures (5 rows)", "HOS measure definitions: fall risk, monitoring activity, physical health, mental health, physical activity"),
    bulletBold("gold_hos_scorecard (70 rows)", "Per-contract HOS performance: rate, 4-star cut-point, star rating, survey statistics, AWV percentage"),
    bulletBold("gold_hos_members (~14,000 rows)", "Member-level urgency scoring (15-98) with risk level, handler assignment, comorbidities, homebound flag"),
    bulletBold("gold_hos_provider_scorecard (~1,000 rows)", "Provider-level gap counts per HOS measure for targeted provider engagement"),
    spacer(40),

    h2("3.5 Market Reference Tables (stars_gold schema)"),
    p("Three tables provide CMS public dataset benchmarks for competitive market analysis:"),
    bulletBold("cms_plan_enrollment_history", "Historical enrollment by contract and year (2021-2025)"),
    bulletBold("cms_plan_star_history", "Historical overall star ratings with organization and state"),
    bulletBold("cms_measure_star_history", "Historical measure-level star ratings by domain"),
    spacer(40),

    h2("3.6 Delta Lake Optimization Strategy"),
    p("The following optimization techniques are applied across the medallion layers:"),
    bulletBold("Partition Pruning", "silver_claim partitioned by service_month; silver_pharmacy_fill partitioned by fill_month. Enables month-level scan elimination for temporal queries."),
    bulletBold("Z-Ordering", "gold_member_gap Z-ordered on (plan_key, measure_code) for multi-dimensional gap analysis. gold_measure_scorecard Z-ordered on (plan_key, measurement_year)."),
    bulletBold("Auto Optimize", "Spark config spark.databricks.delta.optimizeWrite.enabled = true and spark.databricks.delta.autoCompact.enabled = true on all pipeline clusters."),
    bulletBold("Liquid Clustering", "Candidate: gold_member_gap on (plan_key, measure_code, propensity_score) for adaptive co-location as access patterns evolve."),
    bulletBold("VACUUM", "Weekly VACUUM with 7-day retention to reclaim storage from expired Delta versions."),
    bulletBold("Delta Statistics", "Column-level min/max/null statistics maintained for all tables to enable data skipping."),
    pageBreak(),
  ];
  return content;
}

// ── SECTION 4: DATA PIPELINE ─────────────────────────────────────────────────
function section4() {
  return [
    h1("4. Data Pipeline & Processing"),

    h2("4.1 Pipeline Overview"),
    p("The StarPulse data pipeline consists of 14 Databricks notebooks organized across three medallion layers. All notebooks are parameterized via dbutils.widgets for catalog name, seed values, member counts, and measurement year, enabling environment-agnostic execution across dev/staging/production workspaces."),

    h2("4.2 Pipeline Dependency DAG"),
    p("The following diagram shows the execution dependency graph. Bronze tasks execute in parallel (no interdependencies). Silver tasks depend on their Bronze sources. Gold tasks depend on their required Silver dimensions and facts."),
    spacer(40),
    ...monoBlock([
      "BRONZE (Parallel)              SILVER (Sequential)          GOLD (Dependencies)",
      "==================             ===================          ====================",
      "",
      "01_bronze_enrollment --------> 06_silver_member_plan -----> 09_gold_star_ratings",
      "                                     |                      10_gold_measure_scorecard",
      "02_bronze_claims ----+              |                      11_gold_member_gaps",
      "03_bronze_pharmacy --+--> 08_silver_clinical_events -----> 12_gold_cahps_teamview",
      "05_bronze_call_ctr --+         |                           13_gold_campaigns_alerts",
      "                               |                           14_gold_hos",
      "04_bronze_cahps -------> 07_silver_measure_cahps -------->",
      "",
      "Total: 5 Bronze | 3 Silver | 6 Gold = 14 tasks",
      "Critical path: bronze_enrollment -> silver_member_plan -> silver_clinical_events -> gold_member_gaps",
    ]),
    spacer(80),

    h2("4.3 Workflow Orchestration"),
    p("Pipeline execution is managed by a Databricks Multi-Task Workflow with the following configuration:"),
    makeTable(
      ["Property", "Value"],
      [
        ["Workflow Name", "stars_medallion_pipeline"],
        ["Schedule", "Daily at 6:00 AM Eastern (quartz: 0 0 6 * * ?)"],
        ["Cluster Type", "Job Cluster (auto-terminated)"],
        ["Instance Type", "m5d.large (2 workers)"],
        ["Spark Version", "14.3.x-scala2.12 (Spark 3.5.0)"],
        ["Libraries", "faker==24.0.0, numpy==1.26.4 (PyPI)"],
        ["Max Retries", "1 per task (60-second retry interval)"],
        ["Timeout", "30 min (Bronze), 90 min (Silver clinical), 60 min (Gold gaps)"],
        ["Notifications", "Email on success and failure"],
        ["Format", "MULTI_TASK"],
      ],
      [3000, 6360]
    ),
    spacer(80),

    h2("4.4 Data Volume Summary"),
    makeTable(
      ["Layer", "Table", "Row Count", "Write Mode"],
      [
        ["Bronze", "bronze_enrollment_raw", "100,000", "Overwrite"],
        ["Bronze", "bronze_claims_raw", "1,800,000", "Overwrite (200K chunks)"],
        ["Bronze", "bronze_pharmacy_raw", "1,100,000", "Overwrite (200K chunks)"],
        ["Bronze", "bronze_cahps_survey_raw", "~120,000", "Overwrite"],
        ["Bronze", "bronze_call_center_raw", "375,000", "Overwrite (100K chunks)"],
        ["Silver", "silver_member", "100,000", "Overwrite"],
        ["Silver", "silver_plan", "28", "Overwrite"],
        ["Silver", "silver_provider", "12,000", "Overwrite"],
        ["Silver", "silver_measure", "45", "Overwrite"],
        ["Silver", "silver_cahps_response", "~120,000", "Overwrite"],
        ["Silver", "silver_claim", "~1,800,000", "Overwrite (partitioned by service_month)"],
        ["Silver", "silver_pharmacy_fill", "~1,100,000", "Overwrite (partitioned by fill_month)"],
        ["Silver", "silver_outreach_event", "~120,000", "Overwrite (100K chunks)"],
        ["Silver", "silver_call_event", "~375,000", "Overwrite"],
        ["Gold", "gold_star_rating_summary", "14", "Overwrite"],
        ["Gold", "gold_measure_scorecard", "1,260", "Overwrite"],
        ["Gold", "gold_member_gap", "~260,000", "Overwrite (100K chunks)"],
        ["Gold", "gold_cahps_overview", "14", "Overwrite"],
        ["Gold", "gold_team_view", "6", "Overwrite"],
        ["Gold", "gold_campaign_performance", "180", "Overwrite"],
        ["Gold", "gold_alert_priority", "~20", "Overwrite"],
        ["Gold", "gold_intervention_hub", "10", "Overwrite"],
        ["Gold", "gold_hos_measures", "5", "Overwrite"],
        ["Gold", "gold_hos_scorecard", "70", "Overwrite"],
        ["Gold", "gold_hos_members", "~14,000", "Overwrite"],
        ["Gold", "gold_hos_provider_scorecard", "~1,000", "Overwrite"],
      ],
      [1200, 3200, 1800, 3160]
    ),
    spacer(80),

    h2("4.5 Key Transformation Logic"),
    bulletBold("PII Hashing (Silver)", "SHA-256 applied to synthetic_mbi, phone, and email in silver_member. display_name reduced to first name + last initial only. No reversible PII stored in Silver or Gold layers."),
    bulletBold("Top-Box Computation (Silver CAHPS)", "Likert scale: response >= 4 (Always) = top-box. Rating-10: response >= 9 = top-box. Aligns with CMS CAHPS methodology."),
    bulletBold("Utilization Segmentation", "Random assignment weighted: Low 35%, Moderate 40%, Chronic 20%, Very High Risk 5%. High-risk segments receive +0-2 additional gaps."),
    bulletBold("Propensity Score Generation", "Uniform distribution (20.0-95.0) with channel thresholds: >75 = Call, >40 = SMS, else Email. Incentive: >80 = None, >60 = $25 card, else $50 card."),
    bulletBold("Status Classification", "Green: rate >= 4-star threshold + 5pts. Yellow: rate >= 4-star threshold - 8pts. Red: rate < 4-star threshold - 8pts."),
    bulletBold("Alert Generation", "Auto-computed from gold_measure_scorecard: severity = critical if gap > 15pts or status = red; warning if gap > 5pts or status = yellow; info otherwise."),
    spacer(40),

    h2("4.6 Error Handling & Idempotency"),
    p("All pipeline notebooks use Delta Lake mode('overwrite') with overwriteSchema='true', ensuring fully idempotent re-runs. Failed tasks can be retried without manual cleanup. Large datasets are written in chunks (100K-200K rows) to prevent out-of-memory errors on worker nodes."),
    p("At the API layer, every router wraps its Databricks SQL query in a try/except block. On any connection failure, the endpoint returns pre-defined fallback data with identical schema, ensuring the frontend remains functional regardless of backend state."),

    h2("4.7 Data Quality Validations"),
    bullet("Row count assertions: each notebook prints final row counts for runtime verification"),
    bullet("Distribution checks: groupBy aggregations displayed after key transformations (gap_status, composite_code, utilization_segment)"),
    bullet("Referential integrity: Silver notebooks join on member_id to member_map, dropping orphan records via left join"),
    bullet("Schema validation: explicit StructType schemas prevent silent type coercion"),
    bullet("Connection status endpoint: GET /api/connection-status queries gold_star_rating_summary to verify end-to-end pipeline health"),
    pageBreak(),
  ];
}

// ── SECTION 5: ML & AI COMPONENTS ────────────────────────────────────────────
function section5() {
  return [
    h1("5. Machine Learning & AI Components"),

    h2("5.1 Current Analytical Foundation"),
    p("StarPulse implements a rule-based analytical engine as the operational baseline, with the architecture designed to accommodate trained ML models as they mature through the development lifecycle."),
    spacer(40),

    h3("5.1.1 Star Rating Calculator"),
    p("The star_calculator.py service computes weighted overall star ratings from individual measure rates. Each of the 14 HEDIS measures has a defined 4-star threshold, 5-star threshold, and CMS weight:"),
    makeTable(
      ["Measure", "Weight", "4-Star Threshold", "5-Star Threshold", "Status Logic"],
      [
        ["HBD (Blood Sugar)", "3x", "80.0%", "90.0%", "Green >= 85, Yellow >= 72, Red < 72"],
        ["CBP (Blood Pressure)", "3x", "70.0%", "80.0%", "Green >= 75, Yellow >= 62, Red < 62"],
        ["PCR (Readmissions)", "3x", "75.0%", "85.0%", "Green >= 80, Yellow >= 67, Red < 67"],
        ["BCS (Breast Cancer)", "1x", "72.0%", "82.0%", "Green >= 77, Yellow >= 64, Red < 64"],
        ["COL (Colorectal)", "1x", "68.0%", "78.0%", "Green >= 73, Yellow >= 60, Red < 60"],
        ["COA_MR (Medication Review)", "1x", "82.0%", "90.0%", "Green >= 87, Yellow >= 74, Red < 74"],
        ["COA_PA (Pain Assessment)", "1x", "74.0%", "84.0%", "Green >= 79, Yellow >= 66, Red < 66"],
        ["OMW (Osteoporosis)", "1x", "62.0%", "72.0%", "Green >= 67, Yellow >= 54, Red < 54"],
        ["EED (Eye Exam)", "1x", "70.0%", "80.0%", "Green >= 75, Yellow >= 62, Red < 62"],
        ["KED (Kidney Eval)", "1x", "65.0%", "75.0%", "Green >= 70, Yellow >= 57, Red < 57"],
        ["MRP (Med Reconciliation)", "1x", "86.0%", "94.0%", "Green >= 91, Yellow >= 78, Red < 78"],
        ["SPC (Statin Therapy)", "1x", "68.0%", "78.0%", "Green >= 73, Yellow >= 60, Red < 60"],
        ["TRC (Transitions of Care)", "1x", "70.0%", "80.0%", "Green >= 75, Yellow >= 62, Red < 62"],
        ["AMM (ED Follow-up)", "1x", "64.0%", "74.0%", "Green >= 69, Yellow >= 56, Red < 56"],
      ],
      [2200, 800, 1600, 1600, 3160]
    ),
    spacer(80),
    p("Overall star rating formula: weighted_sum = SUM(measure_stars * measure_weight) / SUM(measure_weight), rounded to nearest 0.5."),
    spacer(40),

    h3("5.1.2 Simulator Engine"),
    p("The simulator_engine.py service projects gap closure outcomes based on channel selection, incentive type, and member filtering. Core parameters:"),
    bulletBold("Baseline Closure Rates", "Call: 28%, SMS: 22%, Email: 12%"),
    bulletBold("Incentive Boost", "None: +0%, $25 card: +4%, $50 card: +8%"),
    bulletBold("Cost Model", "Call: $22/member, SMS: $4/member, Email: $2/member + incentive cost"),
    bulletBold("Waterfall Distribution", "4-week rollout: Week 1 (40%), Week 2 (30%), Week 3 (20%), Week 4 (10%)"),
    bulletBold("Gap Weights", "Open: 55%, Partial: 30%, Borderline: 15% of eligible pool"),
    bulletBold("Propensity Weights", "High: 25%, Medium: 42%, Low: 33% of eligible pool"),
    bulletBold("Suppressions", "Recently contacted: 83 members, Opted out: 29, Already closed: 41"),
    spacer(40),

    h3("5.1.3 Propensity Scoring"),
    p("Current propensity scores are generated during gold_member_gap creation as uniform random values (20.0-95.0). Channel routing thresholds: >75 = Call (high-touch, highest closure rate), >40 = SMS (medium-touch, moderate cost), <40 = Email (low-touch, lowest cost but broadest reach)."),
    spacer(40),

    h2("5.2 ML Model Architecture (Production Design)"),
    p("The platform architecture supports the following trained ML models, designed to replace rule-based heuristics with data-driven predictions:"),
    spacer(40),

    h3("5.2.1 Member Propensity Model"),
    bulletBold("Algorithm", "XGBoost gradient-boosted classifier"),
    bulletBold("Objective", "Predict probability of gap closure per member-measure combination"),
    bulletBold("Features", "Demographics (age, gender, utilization_segment), claims history (frequency, recency, ICD-10 categories), pharmacy adherence (PDC, days_supply patterns), outreach history (response_status distribution, channel responsiveness), prior gap closure rate"),
    bulletBold("Training Data", "silver_member + silver_claim + silver_pharmacy_fill + silver_outreach_event + gold_member_gap (historical closed gaps as positive labels)"),
    bulletBold("Output", "Probability score (0.0-1.0) replacing the current uniform random propensity"),
    bulletBold("Refresh Cadence", "Weekly retrain on latest 90-day window"),
    spacer(40),

    h3("5.2.2 Closure Rate Predictor"),
    bulletBold("Algorithm", "Random Forest regressor"),
    bulletBold("Objective", "Predict per-member closure probability given channel, incentive, timing, and member characteristics"),
    bulletBold("Integration", "Replaces static CLOSURE_RATES dict in simulator_engine.py with per-member predictions"),
    bulletBold("Features", "Propensity score, channel preference, outreach history, gap duration (days_open), measure complexity (weight), incentive sensitivity"),
    spacer(40),

    h3("5.2.3 Star Rating Forecaster"),
    bulletBold("Algorithm", "Prophet (Facebook) for seasonal decomposition + ARIMA for short-term trend"),
    bulletBold("Objective", "Project end-of-measurement-year compliance rates incorporating intervention lift and seasonal patterns"),
    bulletBold("Input", "Historical measure rates (gold_measure_scorecard over multiple years) + active intervention expected_lift_pct"),
    bulletBold("Output", "Projected rate with confidence intervals, replacing current projected_rate = current_rate + random offset"),
    spacer(40),

    h3("5.2.4 Member Churn Risk Model"),
    bulletBold("Algorithm", "Logistic Regression with L2 regularization"),
    bulletBold("Objective", "Predict probability of member disenrollment within next 90 days"),
    bulletBold("Features", "Enrollment tenure, utilization trend (increasing/decreasing), CAHPS survey sentiment, grievance/appeal history, product_type, dual_eligible_flag"),
    spacer(40),

    h2("5.3 Feature Engineering Pipeline"),
    p("Features are materialized from Silver and Gold layer tables using Databricks Feature Store:"),
    makeTable(
      ["Feature Group", "Source Tables", "Key Features"],
      [
        ["Demographic", "silver_member", "age, gender, state, product_type, dual_eligible, lis_flag, utilization_segment"],
        ["Clinical", "silver_claim", "claims_count_90d, unique_icd10_count, avg_paid_amount, has_chronic_condition, last_claim_recency"],
        ["Pharmacy", "silver_pharmacy_fill", "pdc_ratio, avg_days_supply, drug_class_count, generic_rate, fill_frequency"],
        ["Behavioral", "silver_outreach_event", "total_contacts, response_rate, preferred_channel, avg_contacts_to_close, opt_out_flag"],
        ["Call Center", "silver_call_event", "avg_sentiment, call_frequency, escalation_rate, avg_call_duration"],
        ["Gap History", "gold_member_gap", "current_gap_count, avg_days_open, prior_closure_rate, suppression_flag"],
      ],
      [1800, 3000, 4560]
    ),
    spacer(80),

    h2("5.4 Model Registry & Lifecycle"),
    p("All models are managed through MLflow on Databricks with Unity Catalog integration:"),
    bullet("Experiment Tracking: MLflow experiments with hyperparameter logging, metric tracking (AUC, precision, recall), and artifact storage"),
    bullet("Model Registry: Unity Catalog model registry with staging/production promotion workflow"),
    bullet("Model Serving: Databricks Model Serving endpoints for real-time inference at API query time"),
    bullet("Monitoring: Data drift detection on feature distributions, prediction drift on output distributions, automated retraining triggers"),
    bullet("A/B Testing: Canary deployment with traffic splitting between current rule-based engine and ML predictions"),
    spacer(40),
    ...monoBlock([
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
    pageBreak(),
  ];
}

// ── SECTION 6: GENAI INTEGRATION ─────────────────────────────────────────────
function section6() {
  return [
    h1("6. Generative AI Integration Architecture"),

    h2("6.1 GenAI Use Cases in StarPulse"),
    p("StarPulse leverages Generative AI across multiple platform capabilities, positioning the solution as AI-first for healthcare quality management:"),
    makeTable(
      ["Use Case", "UI Location", "GenAI Capability"],
      [
        ["AI Copilot", "Agent Execution page", "Real-time resolution guidance during live member calls with context-aware scripts"],
        ["NL Insights", "Executive & HEDIS pages", "Natural language explanations of KPI changes and measure performance trends"],
        ["Intervention Recommendations", "CAHPS Interventions tab", "AI-generated process improvement suggestions with expected lift projections"],
        ["Alert Narratives", "Alerts & Priorities page", "Auto-generated alert descriptions with contextual metrics and action recommendations"],
        ["Conversational Analytics", "Platform-wide", "Natural language to SQL translation for ad-hoc analytical queries"],
        ["Member Outreach Scripts", "Agent Execution page", "Personalized outreach templates with member-specific context variables"],
        ["Anomaly Explanations", "HEDIS & CAHPS pages", "AI-driven explanations for unexpected measure rate changes"],
        ["Dashboard Summaries", "Executive Overview", "Auto-generated narrative summaries of portfolio performance"],
      ],
      [2400, 2800, 4160]
    ),
    spacer(80),

    h2("6.2 RAG Architecture"),
    p("The Retrieval-Augmented Generation (RAG) pipeline grounds LLM responses in authoritative healthcare regulatory documents, ensuring factual accuracy for Medicare Stars domain-specific queries:"),
    spacer(40),
    ...monoBlock([
      "RAG PIPELINE ARCHITECTURE",
      "",
      "+------------+    +------------+    +--------------+    +------------+",
      "| User Query | -> | Intent     | -> | Document     | -> | Context    |",
      "|            |    | Classifier |    | Retrieval    |    | Assembly   |",
      "+------------+    +------------+    +--------------+    +------------+",
      "                                         |                    |",
      "                                    +---------+          +--------+",
      "                                    | Vector  |          | LLM    |",
      "                                    | Search  |          | (Claude/",
      "                                    | Index   |          |  GPT-4)|",
      "                                    +---------+          +--------+",
      "                                         |                    |",
      "                                    +---------+          +--------+",
      "                                    | CMS Tech|          | Output |",
      "                                    | Notes   |          | Parser |",
      "                                    | HEDIS   |          | (JSON) |",
      "                                    | Specs   |          +--------+",
      "                                    +---------+               |",
      "                                                         +--------+",
      "                                                         | UI     |",
      "                                                         | Render |",
      "                                                         +--------+",
    ]),
    spacer(80),

    h3("6.2.1 Document Store"),
    bullet("CMS Star Rating Technical Notes (annual publication, ~200 pages)"),
    bullet("HEDIS Technical Specifications Volume 2 (measure-specific logic)"),
    bullet("CAHPS Survey Administration protocols"),
    bullet("HOS Survey methodology and cut-point documentation"),
    bullet("Internal intervention playbooks and best practice guides"),
    spacer(40),

    h3("6.2.2 Embedding & Retrieval"),
    bulletBold("Embedding Model", "Databricks Foundation Model (BGE-large-en-v1.5) for dense vector representations"),
    bulletBold("Vector Store", "Databricks Vector Search with Delta Sync index for automatic refresh on document updates"),
    bulletBold("Chunk Strategy", "512-token chunks with 64-token overlap, preserving section boundaries"),
    bulletBold("Similarity Search", "Top-5 retrieval with MMR (Maximal Marginal Relevance) for diversity"),
    spacer(40),

    h2("6.3 Prompt Orchestration"),
    p("LangChain-based prompt chains compose domain-specific context for each GenAI use case:"),
    bulletBold("System Prompt", "Includes plan-specific context (contract_id, current rates, gap counts, QBP at stake) injected from gold layer tables"),
    bulletBold("Few-Shot Examples", "Historical intervention outcomes and their measured impact serve as in-context learning examples"),
    bulletBold("Output Parsing", "Structured JSON output schemas enforce consistent response format for direct UI component consumption"),
    bulletBold("Guard Rails", "Response validation against known measure codes and rate ranges; hallucination detection via retrieval confidence scores"),
    spacer(40),

    h2("6.4 Natural Language to SQL Engine"),
    p("The NL-to-SQL capability enables business users to query the data warehouse using conversational language:"),
    bullet("Schema-aware prompts include table and column metadata from Unity Catalog information_schema"),
    bullet("Query generation restricted to SELECT statements only (read-only safety)"),
    bullet("Parameterized execution prevents SQL injection"),
    bullet("Result size limits (1,000 rows max) prevent resource exhaustion"),
    bullet("Query explanation: each generated SQL is accompanied by a plain-English description of what it retrieves"),
    spacer(40),

    h2("6.5 GenAI Pipeline in Databricks"),
    p("The GenAI services layer runs within the Databricks ecosystem:"),
    bullet("Foundation Model APIs: Served via Databricks Model Serving for embedding and inference"),
    bullet("Vector Search: Managed Databricks Vector Search indices with automatic Delta table synchronization"),
    bullet("Feature Store Integration: Member and plan context features retrieved from Databricks Feature Store for prompt enrichment"),
    bullet("MLflow Tracking: All prompt chains, retrieval metrics, and generation quality scores logged as MLflow experiments"),
    bullet("Cost Management: Token usage tracking and prompt caching to optimize API costs"),
    pageBreak(),
  ];
}

// ── SECTION 7: SENTIMENT & NLP ───────────────────────────────────────────────
function section7() {
  return [
    h1("7. Sentiment Analysis & NLP Pipeline"),

    h2("7.1 CAHPS Survey Sentiment Analysis"),
    p("The platform processes CAHPS survey responses through a multi-stage NLP pipeline that converts raw survey data into actionable quality improvement insights."),
    spacer(40),

    h3("7.1.1 Quantitative Foundation (Current)"),
    p("The silver_cahps_response table computes top-box flags using CMS-standard methodology:"),
    bullet("Likert scale (1-4): top_box_flag = True when response_value >= 4 (Always)"),
    bullet("Rating-10 scale (0-10): top_box_flag = True when response_value >= 9"),
    bullet("Response distribution weights: Likert skewed toward 3-4 (35%/45%); Rating-10 skewed toward 7-10"),
    bullet("Top-box rates by composite: GCQ ~80%, DC ~82%, CS ~75%, HPR ~68%, GNC ~80%, CC ~72%"),
    spacer(40),

    h3("7.1.2 NLP Enhancement (Designed)"),
    p("Free-text survey responses and call transcripts are processed through a healthcare-adapted NLP classification pipeline:"),
    makeTable(
      ["Classification Label", "Description", "Trigger Criteria"],
      [
        ["Positive", "Member reports satisfaction with care experience", "Sentiment score > 0.5, no complaint keywords"],
        ["Neutral", "Factual or mixed feedback without strong sentiment", "Sentiment score -0.2 to 0.5"],
        ["Negative", "Member reports dissatisfaction or care gaps", "Sentiment score < -0.2 or complaint keywords detected"],
        ["Risk Escalation", "Urgent safety or quality concern requiring immediate intervention", "Keywords: harm, unsafe, emergency, wrong medication, fall"],
      ],
      [2000, 3500, 3860]
    ),
    spacer(80),

    h2("7.2 Call Center Sentiment Pipeline"),
    p("The bronze_call_center_raw table includes a sentiment_score field (-1.0 to +1.0) that flows through to silver_call_event. Sentiment is correlated with call disposition:"),
    bullet("Reached - Scheduled: positive sentiment (0.1 to 1.0)"),
    bullet("Opted Out: negative sentiment (-1.0 to -0.2)"),
    bullet("No Answer / Voicemail: neutral sentiment (-0.3 to 0.3)"),
    spacer(40),
    p("The designed real-time pipeline adds:"),
    bullet("Speech-to-text transcription of live calls via Databricks streaming"),
    bullet("Real-time sentiment scoring with rolling window averages"),
    bullet("Agent assist copilot that surfaces resolution scripts based on detected member sentiment"),
    bullet("Negative sentiment call rate tracking: current 18%, target 8% (tracked in CAHPS Interventions)"),
    spacer(40),

    h2("7.3 Healthcare-Specific NLP"),
    bulletBold("Domain Adaptation", "Fine-tuned models on Medicare-specific vocabulary: measure codes (HBD, CBP, COL), plan terminology (QBP, AWV, PDC), and clinical concepts (ICD-10, CPT)"),
    bulletBold("Entity Extraction", "Named entity recognition for: provider names, medication names, condition mentions, date expressions, and measure references in unstructured text"),
    bulletBold("Intent Classification", "Member outreach response intents: schedule_appointment, request_callback, decline, opt_out, already_completed, need_transportation"),
    spacer(40),

    h2("7.4 Feedback-to-Insight Conversion"),
    p("CAHPS survey themes are systematically mapped to actionable interventions through the following pipeline:"),
    bullet("6 CAHPS composites (GNC, GCQ, DC, CS, HPR, CC) are linked to 6 departments via gold_team_view"),
    bullet("Department owners (Clinical Quality, Member Experience, Call Center, Pharmacy, Utilization Mgmt, Network) receive composite-specific action items"),
    bullet("gold_intervention_hub tracks 10 named programs with expected lift percentages (1.5% - 4.1%)"),
    bullet("Negative sentiment interactions trigger structured service recovery outreach programs"),
    bullet("Weekly sentiment trend reports surface emerging quality themes before they impact star ratings"),
    pageBreak(),
  ];
}

// ── SECTION 8: PREDICTIVE INTELLIGENCE ───────────────────────────────────────
function section8() {
  return [
    h1("8. Predictive Intelligence Layer"),

    h2("8.1 Gap Closure Prediction"),
    h3("8.1.1 Current Implementation"),
    p("The simulator engine uses static closure rates per channel with incentive boost modifiers:"),
    p("closure_rate(channel, incentive) = CLOSURE_RATES[channel] + INCENTIVE_BOOST[incentive]"),
    p("Example: Call channel + $25 card = 0.28 + 0.04 = 0.32 (32% expected closure rate)"),
    spacer(40),
    p("Net pool calculation:"),
    p("gross_pool = open_gaps x gap_scale x prop_scale"),
    p("suppression_scaled = suppression_total x (gross_pool / open_gaps)"),
    p("net_pool = gross_pool - suppression_scaled"),
    p("total_closures = net_pool x closure_rate"),
    p("projected_rate = current_rate + (total_closures / eligible x 100)"),
    spacer(40),

    h3("8.1.2 Enhanced Prediction"),
    p("Production enhancement replaces static rates with per-member predicted closure probabilities:"),
    bullet("XGBoost model predicts individual member closure probability given member features + channel + incentive"),
    bullet("Simulator aggregates individual predictions for cohort-level projections"),
    bullet("Confidence intervals provided for each projection (p10, p50, p90)"),
    bullet("Historical campaign performance (180 records in gold_campaign_performance) serves as training/validation data"),
    spacer(40),

    h2("8.2 Star Rating Projection"),
    h3("8.2.1 Current Implementation"),
    p("Projected rates in gold_measure_scorecard are generated as: projected_rate = current_rate + random.uniform(0.5, 3.5) for non-H3312 contracts, with H3312 using fixed reference values."),
    spacer(40),
    h3("8.2.2 Enhanced Forecasting"),
    bullet("Time-series decomposition using Prophet for seasonal trends in measure rates"),
    bullet("Intervention lift incorporation: each active intervention in gold_intervention_hub contributes its expected_lift_pct to the projection"),
    bullet("Monte Carlo simulation for star rating probability distributions (probability of reaching 4.0)"),
    bullet("What-if analysis: model the impact of starting/stopping specific interventions on projected stars"),
    spacer(40),

    h2("8.3 Risk Stratification"),
    h3("8.3.1 Current Implementation"),
    p("The utilization_segment field in silver_member assigns members to risk tiers: Low (35%), Moderate (40%), Chronic (20%), Very High Risk (5%). HOS urgency scores (15-98) incorporate 7 weighted factors for fall risk assessment."),
    spacer(40),
    h3("8.3.2 Enhanced Risk Models"),
    bulletBold("Patient Risk Prediction", "Claims-based HCC (Hierarchical Condition Category) risk scoring using ICD-10 diagnosis history from silver_claim"),
    bulletBold("Readmission Prediction", "30-day readmission risk model using PCR measure data and transition-of-care history"),
    bulletBold("Provider Performance Forecasting", "Provider-level gap closure rate prediction based on gold_hos_provider_scorecard patterns"),
    bulletBold("Cost Forecasting", "Per-member cost projection using claims trend analysis and pharmacy utilization patterns"),
    bulletBold("Claim Anomaly Detection", "Isolation Forest algorithm on claim amount distributions to flag billing anomalies"),
    spacer(40),

    h2("8.4 Feature Store Design"),
    p("Centralized feature computation leveraging Databricks Feature Store:"),
    makeTable(
      ["Feature Group", "Update Frequency", "Storage", "Key Features"],
      [
        ["Demographics", "Daily", "Online + Offline", "age, gender, risk_segment, dual_eligible, enrollment_tenure"],
        ["Clinical (90-day)", "Daily", "Online + Offline", "claims_count, unique_dx_count, er_visits, inpatient_stays, chronic_conditions"],
        ["Pharmacy (PDC)", "Daily", "Online + Offline", "pdc_ratio, drug_class_diversity, fill_adherence_trend, generic_rate"],
        ["Behavioral", "Daily", "Online + Offline", "outreach_response_rate, preferred_channel, opt_out_flag, avg_contacts_to_close"],
        ["Sentiment", "Real-time", "Online", "rolling_30d_sentiment, negative_call_rate, survey_top_box_rate"],
        ["Gap Context", "Daily", "Offline", "gap_count, avg_days_open, historical_closure_rate, measure_complexity"],
      ],
      [2000, 1600, 2000, 3760]
    ),
    pageBreak(),
  ];
}

// ── SECTION 9: SECURITY & GOVERNANCE ─────────────────────────────────────────
function section9() {
  return [
    h1("9. Security & Governance"),

    h2("9.1 Data Classification"),
    makeTable(
      ["Classification", "Examples", "Handling"],
      [
        ["PHI (Protected Health Information)", "Member MBI, diagnosis codes, medication details, claim amounts", "SHA-256 hashing in Silver layer; column-level masking via Unity Catalog"],
        ["PII (Personally Identifiable Information)", "Member name, DOB, phone, email, address", "Hashed in Silver; display_name reduced to first name + last initial"],
        ["Clinical", "Claims, pharmacy fills, call center records", "Aggregated in Gold layer; no individual clinical detail exposed to UI"],
        ["Operational", "Campaign metrics, alert priorities, team assignments", "Available to authorized application users"],
      ],
      [2400, 3000, 3960]
    ),
    spacer(80),

    h2("9.2 PII Protection Implementation"),
    p("The Silver layer (notebook 06_silver_member_plan.py) applies systematic PII protection:"),
    bullet("member_mbi_hash = SHA-256(synthetic_mbi) - irreversible hash of Medicare Beneficiary Identifier"),
    bullet("phone_hash = SHA-256(member_id + '_phone') - irreversible hash of phone number"),
    bullet("email_hash = SHA-256(member_id + '_email') - irreversible hash of email address"),
    bullet("display_name = first_name + ' ' + last_name[0] + '.' - reduced to non-identifying form"),
    bullet("No Bronze-layer PII is accessible from the API layer; only Silver and Gold tables are queried"),
    spacer(40),

    h2("9.3 Unity Catalog Governance"),
    p("Three-level namespace provides granular access control:"),
    bulletBold("Catalog Level", "aiagenticdemo - single catalog containing all platform data"),
    bulletBold("Schema Level", "stars_bronze (raw), stars_silver (curated), stars_gold (analytics + CMS reference) - schema-level grants control read/write access"),
    bulletBold("Table Level", "Individual table grants for sensitive objects (e.g., silver_member restricted to Data Engineering role)"),
    bullet("Data lineage automatically tracked across all medallion transformations"),
    bullet("Audit logs capture all data access events with user identity, timestamp, and query text"),
    spacer(40),

    h2("9.4 Role-Based Access Control (RBAC)"),
    makeTable(
      ["Role", "Bronze", "Silver", "Gold", "API", "Dashboard"],
      [
        ["Data Engineer", "Read/Write", "Read/Write", "Read/Write", "N/A", "N/A"],
        ["Data Analyst", "No Access", "Read Only", "Read Only", "N/A", "Full Access"],
        ["App Service Account", "No Access", "Read Only", "Read Only", "Full Access", "N/A"],
        ["Executive User", "No Access", "No Access", "No Access", "N/A", "View Only"],
        ["Security Admin", "Audit Only", "Audit Only", "Audit Only", "Audit Only", "Audit Only"],
      ],
      [2200, 1200, 1200, 1400, 1200, 2160]
    ),
    spacer(80),

    h2("9.5 Row-Level Security"),
    p("Contract-level data isolation is enforced at multiple layers:"),
    bullet("API layer: Most endpoints accept contract_id as a query parameter, filtering results to a single contract"),
    bullet("Gold tables: gold_star_rating_summary, gold_measure_scorecard, gold_member_gap all include plan_key for row-level filtering"),
    bullet("Unity Catalog: Dynamic views can enforce row-level security policies based on user group membership"),
    bullet("Frontend: Contract selector dropdown limits visible data to user-authorized contracts"),
    spacer(40),

    h2("9.6 API Security"),
    p("Current deployment security:"),
    bullet("CORS middleware configured for Databricks Apps domain"),
    bullet("Databricks Apps provides built-in authentication and TLS termination"),
    bullet("Connection-status endpoint validates backend connectivity without exposing credentials"),
    spacer(40),
    p("Production hardening:"),
    bullet("OAuth 2.0 / JWT token-based authentication for API access"),
    bullet("API key management with rotation policies"),
    bullet("Rate limiting per client to prevent abuse"),
    bullet("Request logging with audit trail"),
    spacer(40),

    h2("9.7 HIPAA Compliance Considerations"),
    makeTable(
      ["HIPAA Requirement", "Platform Control"],
      [
        ["Access Controls (164.312(a)(1))", "Unity Catalog RBAC, row-level security, API authentication"],
        ["Audit Controls (164.312(b))", "Delta Lake time travel, Unity Catalog audit logs, API request logging"],
        ["Integrity Controls (164.312(c)(1))", "Delta Lake ACID transactions, schema enforcement, data quality validations"],
        ["Transmission Security (164.312(e)(1))", "TLS encryption in transit (Databricks Apps auto-TLS), encrypted connections"],
        ["Person Authentication (164.312(d))", "Databricks workspace SSO, API token authentication"],
        ["PHI De-identification", "SHA-256 hashing of MBI/phone/email in Silver layer, display_name masking"],
        ["Minimum Necessary", "Gold layer provides only aggregated/de-identified data to application; no raw PHI exposed"],
        ["Encryption at Rest", "Databricks managed encryption for Delta Lake storage (AWS S3 SSE)"],
      ],
      [3500, 5860]
    ),
    spacer(80),

    h2("9.8 Audit Trail"),
    p("Multiple audit mechanisms operate across the platform:"),
    bulletBold("Bronze Layer", "raw_source and ingestion_ts columns on every record identify data provenance"),
    bulletBold("Gold Layer", "last_updated timestamps on gold_star_rating_summary, gold_measure_scorecard, gold_cahps_overview"),
    bulletBold("Delta Lake", "Time travel enables point-in-time queries on any table version; DESCRIBE HISTORY shows all mutations"),
    bulletBold("Unity Catalog", "System tables capture all access events, permission changes, and schema modifications"),
    bulletBold("API Layer", "FastAPI middleware logs request method, path, response status, and execution time"),
    pageBreak(),
  ];
}

// ── SECTION 10: SCALABILITY ──────────────────────────────────────────────────
function section10() {
  return [
    h1("10. Scalability & Performance"),

    h2("10.1 Current Data Volumes"),
    makeTable(
      ["Metric", "Value"],
      [
        ["Total Bronze rows", "~3,395,000"],
        ["Total Silver rows", "~3,632,000"],
        ["Total Gold rows", "~276,579"],
        ["Total member count", "100,000 across 14 contracts"],
        ["Total quality measures", "45 (14 HEDIS + 8 CAHPS + 5 HOS + 5 Part D + 13 Ops)"],
        ["Member-measure gap combinations", "~260,000"],
        ["Historical campaigns", "180"],
        ["Estimated Delta Lake storage", "~2.5 GB compressed"],
      ],
      [4000, 5360]
    ),
    spacer(80),

    h2("10.2 Cluster Strategy"),
    bulletBold("Pipeline Clusters", "Job clusters (m5d.large, 2 workers) auto-created at pipeline start and terminated after completion. Spark 14.3 runtime with Delta Lake preview features enabled."),
    bulletBold("SQL Warehouse", "Serverless SQL Warehouse for API query execution. Auto-scaling from 0 to N clusters based on query concurrency. Auto-suspend after idle period to minimize cost."),
    bulletBold("Databricks Apps", "Serverless compute for FastAPI serving. No cluster management required. Auto-scales with request volume."),
    spacer(40),

    h2("10.3 Query Optimization"),
    bulletBold("Partition Pruning", "silver_claim (service_month) and silver_pharmacy_fill (fill_month) partitions enable month-level scan elimination. Queries with date filters read only relevant partitions."),
    bulletBold("Z-Ordering", "gold_member_gap Z-ordered on (plan_key, measure_code) for multi-dimensional gap queries. gold_measure_scorecard Z-ordered on (plan_key, measurement_year)."),
    bulletBold("Pre-Aggregation", "Gold layer tables are pre-aggregated to the exact grain needed by each API endpoint, eliminating complex joins at query time."),
    bulletBold("Delta Statistics", "Column-level min/max/null statistics enable data skipping, reducing I/O for selective queries."),
    bulletBold("Auto Optimize", "optimizeWrite and autoCompact enabled on pipeline clusters for automatic file consolidation."),
    spacer(40),

    h2("10.4 API Performance"),
    bulletBold("Fallback Pattern", "Every router implements try/except with in-memory fallback data, ensuring sub-100ms response times even during Databricks outages."),
    bulletBold("Frontend Caching", "TanStack Query with configurable staleTime caches API responses in the browser, reducing redundant network requests on page navigation."),
    bulletBold("Connection Pooling", "Databricks SQL connector manages persistent connections with 25-second socket timeout and automatic reconnection."),
    spacer(40),

    h2("10.5 Photon & Serverless Acceleration"),
    bullet("Photon engine accelerates scan-heavy Gold layer queries (aggregations, joins, filters) with native vectorized execution"),
    bullet("Serverless SQL Warehouse eliminates cluster warm-up time for API queries"),
    bullet("Serverless compute for Databricks Apps provides automatic horizontal scaling for web serving"),
    spacer(40),

    h2("10.6 Cost Optimization"),
    bullet("Job clusters auto-terminate after pipeline completion (no idle compute costs)"),
    bullet("SQL Warehouse auto-suspends during low-traffic periods"),
    bullet("Delta Lake VACUUM reclaims storage from expired versions (7-day retention)"),
    bullet("Chunked writes (100K-200K rows) prevent memory spikes on worker nodes"),
    bullet("Synthetic data generation uses deterministic seeds, enabling pipeline testing without production data costs"),
    pageBreak(),
  ];
}

// ── SECTION 11: ARCHITECTURE DIAGRAMS ────────────────────────────────────────
function section11() {
  return [
    h1("11. Architecture Diagrams"),
    p("This section consolidates all architectural diagrams with detailed descriptions."),
    spacer(40),

    h2("11.1 Overall Solution Architecture"),
    ...monoBlock([
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
    pageBreak(),

    h2("11.2 Medallion Data Flow"),
    ...monoBlock([
      "BRONZE (Raw)                 SILVER (Curated)              GOLD (Analytics)",
      "========================     ==========================    ========================",
      "",
      "bronze_enrollment_raw   -->  silver_member (PII hashed)    gold_star_rating_summary",
      "  100K members               silver_plan (28 contracts)    gold_measure_scorecard",
      "                             silver_provider (12K)         gold_member_gap (~260K)",
      "                                                           gold_cahps_overview",
      "bronze_claims_raw       -->  silver_claim (~1.8M)          gold_campaign_performance",
      "  1.8M claims                 (partitioned by month)       gold_alert_priority",
      "                                                           gold_intervention_hub",
      "bronze_pharmacy_raw     -->  silver_pharmacy_fill (~1.1M)  gold_team_view",
      "  1.1M Rx fills               (partitioned by month)      ",
      "                                                           gold_hos_measures (5)",
      "bronze_cahps_survey_raw -->  silver_cahps_response         gold_hos_scorecard (70)",
      "  ~120K responses             (top-box computed)           gold_hos_members (~14K)",
      "                             silver_measure (45)           gold_hos_provider (1K)",
      "bronze_call_center_raw  -->  silver_outreach_event (~120K)",
      "  375K calls                 silver_call_event (~375K)     MARKET REF (stars_gold)",
      "                                                           cms_plan_enrollment",
      "                                                           cms_plan_star_history",
      "TOTAL: 3.3M rows            TOTAL: 3.6M+ rows             cms_measure_star_hist",
      "                                                           TOTAL: ~280K rows",
    ]),
    pageBreak(),

    h2("11.3 Pipeline Orchestration DAG"),
    ...monoBlock([
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
    spacer(200),

    h2("11.4 Entity Relationship Diagram"),
    ...monoBlock([
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
    pageBreak(),

    h2("11.5 Frontend Page Architecture"),
    ...monoBlock([
      "React SPA (stars_v2.html - Single File Application)",
      "",
      "+-- Marketing Overview (Hero + Capability Cards)",
      "+-- Executive Overview (KPIs + Plan Table + Filters)",
      "|     +-- Plan Detail (Domain Cards + Historical Ratings)",
      "+-- HEDIS Measures (Sortable Table + Status Filters)",
      "+-- Simulator (Auto Campaign + Human-In-Loop modes)",
      "|     +-- Impact Projector (Measure Sliders)",
      "+-- Agent Execution (Week Tabs + Member Queue + Scripts)",
      "+-- CAHPS Module (5 sub-tabs)",
      "|     +-- Star Overview (Composite Scores)",
      "|     +-- Pulse (Survey Waves)",
      "|     +-- Interventions (AI Recommendations)",
      "|     +-- Team View (Department Accountability)",
      "|     +-- Drilldown (Measure Detail)",
      "+-- HOS Measures (5 Measures + Provider Scorecard)",
      "+-- Campaign History & ROI (Bar + Scatter Charts)",
      "+-- Alerts & Priorities (Priority Board + Alert List)",
      "+-- Member 360 (Gap List + Profile Modal)",
      "+-- EHO4all (LIS/Dual Equity Dashboard)",
      "+-- Market Analysis (Competitive Benchmarking)",
    ]),
    pageBreak(),
  ];
}

// ── SECTION 12: DEMO WALKTHROUGH ─────────────────────────────────────────────
function section12() {
  return [
    h1("12. Demo Walkthrough Narrative"),
    p("This section provides a guided walkthrough of the StarPulse platform, highlighting where data, AI, and predictive intelligence surface throughout the user experience.", { italics: true }),
    spacer(40),

    h2("12.1 Data Journey: From Raw to Insight"),
    p("Consider member MBR-0000042, enrolled in contract H3312 (Health Plan Advantage Premier, FL). Here is how their data flows through the platform:"),
    bullet("Bronze: Enrollment record ingested with demographics, contract assignment (FL), product type (HMO), dual_eligible=false, lis_flag=false"),
    bullet("Silver: PII hashed (MBI, phone, email). display_name set to first name + last initial. Age calculated. Utilization segment assigned based on claims pattern. PCP provider linked."),
    bullet("Gold: Member-measure gap analysis identifies 3 open HEDIS gaps (COL, KED, AMM). Propensity scores calculated: COL=72.4 (SMS), KED=45.1 (SMS), AMM=83.7 (Call). Gap durations: 45-180 days."),
    bullet("Dashboard: Member appears in the Member 360 gap list, sorted by propensity. Clicking their row opens a modal with 5 tabs: Overview, Clinical, Medications, Measures, Claims."),
    spacer(40),

    h2("12.2 Executive View Flow"),
    p("The demo begins at the Marketing Overview page showcasing the EXL | StarPulse brand and five capability domains: HEDIS Clinical Quality, CAHPS Member Experience, HOS Health Outcomes, Medical Adherence, and Admin/Operational."),
    p("Navigating to Executive Overview reveals four portfolio KPIs:"),
    bullet("Total Plans: 14 contracts under management"),
    bullet("Total Enrollment: ~980,000 members"),
    bullet("Contracts Above 4-Star: 9 of 14 (bonus-eligible)"),
    bullet("Portfolio Average: 4.0 stars"),
    p("The contracts table displays all 14 plans with sortable columns for PY Rating, Projected Rating, and domain scores (HEDIS, CAHPS, HOS, Medical Adherence). Filters allow drilling down by state, rating range, or plan name search."),
    spacer(40),

    h2("12.3 HEDIS Deep Dive"),
    p("Clicking into contract H3312 (Health Plan Advantage Premier) on the Plan Detail page reveals:"),
    bullet("Projected overall star rating: 4.0 (displayed as large hero metric)"),
    bullet("Historical ratings: 2021 (3.5) -> 2022 (3.5) -> 2023 (4.0) -> 2024 (4.0) -> 2025 Projected (4.0)"),
    bullet("Four domain cards: HEDIS 3.8, CAHPS 4.2, HOS 4.0, Part D 4.1"),
    p("The HEDIS Measures page shows 14 measures with color-coded status indicators:"),
    bullet("4 Red (Needs Attention): COL at 66.3% (target 68.0%, 5,672 gaps), OMW at 58.9% (target 62.0%, 3,445 gaps), KED at 63.7% (target 65.0%, 4,123 gaps), AMM at 61.4% (target 64.0%, 3,892 gaps)"),
    bullet("6 Yellow (At Risk): CBP 67.8%, BCS 73.4%, COA_PA 76.2%, EED 71.3%, SPC 69.8%, TRC 72.1%"),
    bullet("4 Green (Meets Target): HBD 81.2%, PCR 79.1%, COA_MR 84.5%, MRP 88.4%"),
    p("AI Insight: The platform surfaces that COL has the highest gap count (5,672) and is a 1x-weighted measure, while CBP is 3x-weighted making its 2.2-point gap to target more impactful on overall stars."),
    spacer(40),

    h2("12.4 Simulator Demonstration"),
    p("Navigating to the Campaign Simulator for the COL measure:"),
    bullet("Configure gap filters: Open + Partial (85% of pool)"),
    bullet("Set propensity: High + Medium (67% of pool)"),
    bullet("Select channels: Call + SMS"),
    bullet("Choose incentive: $25 gift card (+4% boost)"),
    p("The simulator calculates in real-time:"),
    bullet("Gross pool: 5,672 x 0.85 x 0.67 = ~3,230 members"),
    bullet("After suppressions: ~2,890 net pool"),
    bullet("Expected closure rate: 32% (Call base 28% + $25 boost 4%)"),
    bullet("Projected closures: ~924 gaps"),
    bullet("Projected rate improvement: 66.3% -> 69.1% (above 4-star threshold of 68.0%)"),
    p("The 4-week waterfall shows: Week 1 (1,156 outreach, 370 closures), Week 2 (867, 277), Week 3 (578, 185), Week 4 (289, 92)."),
    spacer(40),

    h2("12.5 Agent Execution & Outreach"),
    p("The Agent Execution page organizes members into 4-week outreach waves:"),
    bullet("Week 1: High propensity members, first contact via Call/SMS"),
    bullet("Week 2: Non-responders from Week 1 + incentive escalation"),
    bullet("Week 3: Hard-to-reach cases, PCP engagement alerts"),
    bullet("Week 4: Final sweep before measurement snapshot"),
    p("Each member row shows: name, age, propensity %, measure gap, recommended channel, and PCP. Selecting a member opens a scripted outreach template with personalized variables ({name}, {measure}, {pcp})."),
    p("Executing the outreach triggers real Twilio SMS or SendGrid email delivery to the member contact, with response tracking in silver_outreach_event."),
    spacer(40),

    h2("12.6 CAHPS Intelligence"),
    p("The CAHPS module provides five analytical views:"),
    bullet("Star Overview: 6 composites displayed with current/target/gap metrics. Getting Care Quickly (GCQ) at 78.9% flagged for improvement."),
    bullet("Pulse: 9 survey waves with response rates, top-box percentages, and calibration scores tracking intra-year progress."),
    bullet("Interventions: 30+ AI-suggested process improvements tracked by status, owner, and expected impact. Includes NLP-powered agent assist copilot and sentiment-triggered service recovery."),
    bullet("Team View: 6 departments with measure ownership. Clinical Quality owns COL, CBP, KED, OMW, AMM, HBD. Member Experience owns all CAHPS composites."),
    bullet("Drilldown: Composite-specific deep dives with question-level response distributions."),
    spacer(40),

    h2("12.7 Where AI Surfaces"),
    p("At every touchpoint in the demo, AI and predictive intelligence enhance the user experience:"),
    bulletBold("Propensity Scoring", "Members are ranked by closure likelihood, ensuring outreach resources target the highest-probability cases first"),
    bulletBold("Channel Optimization", "Each member receives a channel recommendation based on their predicted responsiveness (Call for high-propensity, SMS for medium, Email for low)"),
    bulletBold("Closure Prediction", "Simulator projects gap closures using channel-specific models, enabling data-driven campaign design"),
    bulletBold("Urgency Scoring", "HOS members are scored 15-98 on urgency factors, routing critical cases to care management teams"),
    bulletBold("NLP Sentiment", "Call center interactions are scored for sentiment, triggering automated service recovery for negative experiences"),
    bulletBold("Intervention AI", "CAHPS improvement suggestions are generated with expected lift percentages, linking member feedback to operational actions"),
    bulletBold("Market Intelligence", "Competitive benchmarking against CMS public datasets provides context for star rating positioning"),
    pageBreak(),
  ];
}

// ── SECTION 13: ASSUMPTIONS ──────────────────────────────────────────────────
function section13() {
  return [
    h1("13. Assumptions & Dependencies"),

    h2("13.1 Data Assumptions"),
    bullet("All data in the current deployment is synthetic, generated using Faker and NumPy with deterministic seeds (seed=42) for reproducibility"),
    bullet("Production deployment requires ETL connections to: claims clearinghouse (EDI 837), pharmacy benefit manager (NCPDP), CAHPS survey vendor (CMS-contracted), call center ACD system"),
    bullet("Member enrollment data assumes 14 contracts across 14 states with realistic enrollment distributions"),
    bullet("HEDIS measure rates and thresholds are based on CMS 2025 Star Rating Technical Notes"),
    spacer(40),

    h2("13.2 Infrastructure Dependencies"),
    bullet("Databricks workspace with Unity Catalog enabled (AWS deployment)"),
    bullet("Serverless SQL Warehouse entitlement for API query execution"),
    bullet("Databricks Apps entitlement for web application hosting"),
    bullet("Databricks Workflows for pipeline orchestration"),
    bullet("S3 storage for Delta Lake managed tables (encrypted at rest)"),
    spacer(40),

    h2("13.3 Third-Party Dependencies"),
    makeTable(
      ["Service", "Purpose", "Configuration"],
      [
        ["Databricks SQL Connector", "Python SDK for SQL Warehouse queries", "databricks-sql-connector==3.4.0"],
        ["Twilio", "SMS outreach delivery", "twilio==9.0.5, requires account SID, auth token, from number"],
        ["SendGrid", "Email outreach delivery", "sendgrid==6.11.0, requires API key and from email"],
        ["FastAPI", "REST API framework", "fastapi==0.111.0 with uvicorn==0.29.0"],
        ["Pydantic", "Request/response validation", "pydantic==2.7.0 with pydantic-settings==2.2.1"],
        ["Faker", "Synthetic data generation", "faker==24.0.0 (pipeline only)"],
        ["NumPy", "Numerical computations", "numpy==1.26.4"],
      ],
      [2800, 2800, 3760]
    ),
    spacer(80),

    h2("13.4 CMS Regulatory Assumptions"),
    bullet("Star rating methodology based on CMS 2025 guidelines; measure weights and cut-points are subject to annual CMS updates"),
    bullet("CAHPS survey administration follows CMS-mandated protocols (12% sampling rate, standardized question sets)"),
    bullet("EHO4all dashboard tracks LIS/Dual disparity metrics as replacement for CAI (Categorical Adjustment Index) effective 2027"),
    bullet("HOS survey methodology includes 2-year longitudinal outcome measures returning to full weight in 2026"),
    spacer(40),

    h2("13.5 Scope Boundaries"),
    bullet("StarPulse manages Stars performance analytics and outreach orchestration only"),
    bullet("Does not replace: claims processing systems, enrollment systems, EHR, pharmacy dispensing, or billing"),
    bullet("Real-time data ingestion (streaming) is not in current scope; pipeline runs daily batch"),
    bullet("ML model training infrastructure (GPU clusters) is designed but not currently provisioned"),
    pageBreak(),
  ];
}

// ── SECTION 14: APPENDICES ───────────────────────────────────────────────────
function section14() {
  return [
    h1("14. Appendices"),

    h2("Appendix A: Complete API Endpoint Reference"),
    makeTable(
      ["Method", "Endpoint", "Parameters", "Response Model"],
      [
        ["GET", "/api/health", "None", "{ status: ok }"],
        ["GET", "/api/connection-status", "None", "{ connected: bool, table_count: int }"],
        ["GET", "/api/star-summary", "None", "StarSummary"],
        ["GET", "/api/plans", "state, py_rating, proj_rating, search", "List[PlanSummary]"],
        ["GET", "/api/plans/{contract_id}", "contract_id (path)", "PlanDetail"],
        ["GET", "/api/hedis-measures", "contract_id, color_filter, sort", "List[HedisMeasure]"],
        ["GET", "/api/cahps", "contract_id", "CahpsOverviewResponse"],
        ["GET", "/api/cahps/pulse", "contract_id", "CahpsPulseResponse"],
        ["GET", "/api/members/gaps", "contract_id, measure_code, gap_status, propensity, page, page_size", "MemberGapPage"],
        ["GET", "/api/members/{member_key}", "member_key (path)", "MemberProfile"],
        ["GET", "/api/campaigns", "status, measure_code", "CampaignResponse"],
        ["GET", "/api/alerts", "None", "AlertsResponse"],
        ["GET", "/api/interventions", "None", "List[InterventionRow]"],
        ["GET", "/api/team-view", "None", "List[TeamViewRow]"],
        ["POST", "/api/simulator/run", "SimulatorConfig (body)", "SimulatorResult"],
        ["GET", "/api/hos/measures", "contract_id", "dict"],
        ["GET", "/api/hos/members", "contract_id, measure_id, risk_filter, handler_filter", "Paginated list"],
        ["GET", "/api/hos/providers", "contract_id, measure_id", "List[Provider]"],
        ["GET", "/api/hos/summary", "contract_id", "HosSummary"],
        ["GET", "/api/market/enrollment", "None", "dict"],
        ["GET", "/api/market/plan-stars", "None", "dict"],
        ["GET", "/api/market/measure-stars", "None", "dict"],
        ["POST", "/api/outreach/send-bundle", "SendBundleRequest (body)", "SendBundleResponse"],
      ],
      [800, 2800, 3000, 2760]
    ),
    spacer(80),

    h2("Appendix B: Quality Measure Reference"),
    p("Complete catalog of 45 measures tracked across the platform:"),
    makeTable(
      ["Code", "Name", "Category", "Part", "Weight"],
      [
        ["HBD", "Diabetes Care - Blood Sugar Controlled", "HEDIS", "C", "3x"],
        ["CBP", "Controlling Blood Pressure", "HEDIS", "C", "3x"],
        ["PCR", "Plan All-Cause Readmissions", "HEDIS", "C", "3x"],
        ["BCS", "Breast Cancer Screening", "HEDIS", "C", "1x"],
        ["COL", "Colorectal Cancer Screening", "HEDIS", "C", "1x"],
        ["COA_MR", "Care for Older Adults - Medication Review", "HEDIS", "C", "1x"],
        ["COA_PA", "Care for Older Adults - Pain Assessment", "HEDIS", "C", "1x"],
        ["OMW", "Osteoporosis Management", "HEDIS", "C", "1x"],
        ["EED", "Diabetes Care - Eye Exam", "HEDIS", "C", "1x"],
        ["KED", "Kidney Health Evaluation", "HEDIS", "C", "1x"],
        ["MRP", "Medication Reconciliation Post-Discharge", "HEDIS", "C", "1x"],
        ["SPC", "Statin Therapy for CVD", "HEDIS", "C", "1x"],
        ["TRC", "Transitions of Care", "HEDIS", "C", "1x"],
        ["AMM", "ED Follow-up for Chronic Conditions", "HEDIS", "C", "1x"],
        ["GNC", "Getting Needed Care", "CAHPS", "C", "2x"],
        ["GCQ", "Getting Care Quickly", "CAHPS", "C", "2x"],
        ["DC", "Doctor Communication", "CAHPS", "C", "2x"],
        ["CS", "Customer Service", "CAHPS", "C", "2x"],
        ["HPR", "Health Plan Rating", "CAHPS", "C", "2x"],
        ["CC", "Care Coordination", "CAHPS", "C", "2x"],
        ["RDP", "Rating of Drug Plan", "CAHPS", "D", "2x"],
        ["GNP", "Getting Needed Prescription Drugs", "CAHPS", "D", "2x"],
        ["DAH", "Med Adherence - Hypertension (RAS)", "PARTD", "D", "3x"],
        ["DAC", "Med Adherence - Cholesterol (Statins)", "PARTD", "D", "3x"],
        ["DAD", "Med Adherence - Diabetes Medications", "PARTD", "D", "3x"],
        ["MTM", "MTM Program Completion Rate", "PARTD", "D", "1x"],
        ["MPM", "Medication Monitoring Chronic Conditions", "PARTD", "D", "1x"],
      ],
      [1200, 4000, 1200, 800, 2160]
    ),
    spacer(80),

    h2("Appendix C: HEDIS 4-Star / 5-Star Thresholds"),
    makeTable(
      ["Measure", "Weight", "4-Star Cut", "5-Star Cut", "Green (>=)", "Yellow Range", "Red (<)"],
      [
        ["HBD", "3x", "80.0%", "90.0%", "85.0%", "72.0% - 85.0%", "72.0%"],
        ["CBP", "3x", "70.0%", "80.0%", "75.0%", "62.0% - 75.0%", "62.0%"],
        ["PCR", "3x", "75.0%", "85.0%", "80.0%", "67.0% - 80.0%", "67.0%"],
        ["BCS", "1x", "72.0%", "82.0%", "77.0%", "64.0% - 77.0%", "64.0%"],
        ["COL", "1x", "68.0%", "78.0%", "73.0%", "60.0% - 73.0%", "60.0%"],
        ["COA_MR", "1x", "82.0%", "90.0%", "87.0%", "74.0% - 87.0%", "74.0%"],
        ["COA_PA", "1x", "74.0%", "84.0%", "79.0%", "66.0% - 79.0%", "66.0%"],
        ["OMW", "1x", "62.0%", "72.0%", "67.0%", "54.0% - 67.0%", "54.0%"],
        ["EED", "1x", "70.0%", "80.0%", "75.0%", "62.0% - 75.0%", "62.0%"],
        ["KED", "1x", "65.0%", "75.0%", "70.0%", "57.0% - 70.0%", "57.0%"],
        ["MRP", "1x", "86.0%", "94.0%", "91.0%", "78.0% - 91.0%", "78.0%"],
        ["SPC", "1x", "68.0%", "78.0%", "73.0%", "60.0% - 73.0%", "60.0%"],
        ["TRC", "1x", "70.0%", "80.0%", "75.0%", "62.0% - 75.0%", "62.0%"],
        ["AMM", "1x", "64.0%", "74.0%", "69.0%", "56.0% - 69.0%", "56.0%"],
      ],
      [1100, 900, 1200, 1200, 1200, 2200, 1560]
    ),
    spacer(80),

    h2("Appendix D: Glossary"),
    makeTable(
      ["Term", "Definition"],
      [
        ["HEDIS", "Healthcare Effectiveness Data and Information Set - standardized quality measures"],
        ["CAHPS", "Consumer Assessment of Healthcare Providers and Systems - patient experience survey"],
        ["HOS", "Health Outcomes Survey - longitudinal health status measurement"],
        ["CMS", "Centers for Medicare & Medicaid Services"],
        ["QBP", "Quality Bonus Payment - revenue bonus for plans rated 4+ stars"],
        ["PDC", "Proportion of Days Covered - medication adherence metric"],
        ["AWV", "Annual Wellness Visit - preventive care encounter"],
        ["MBI", "Medicare Beneficiary Identifier"],
        ["NPI", "National Provider Identifier"],
        ["D-SNP", "Dual-Eligible Special Needs Plan"],
        ["LIS", "Low Income Subsidy (Extra Help for Part D)"],
        ["EHO4all", "Excellent Health Outcomes for All - CMS equity measure (replaces CAI)"],
        ["CAI", "Categorical Adjustment Index (replaced by EHO4all in 2027)"],
        ["ICD-10", "International Classification of Diseases, 10th Revision"],
        ["CPT", "Current Procedural Terminology"],
        ["NDC", "National Drug Code"],
        ["RAG", "Retrieval-Augmented Generation"],
        ["MLflow", "Open-source ML lifecycle management platform"],
        ["Delta Lake", "ACID-compliant data lake storage format"],
        ["Unity Catalog", "Databricks unified governance solution for data and AI"],
      ],
      [1800, 7560]
    ),
    spacer(80),

    h2("Appendix E: Environment Configuration"),
    makeTable(
      ["Variable", "Purpose", "Example"],
      [
        ["DATABRICKS_HOST", "Workspace URL", "https://<workspace>.cloud.databricks.com"],
        ["DATABRICKS_HTTP_PATH", "SQL Warehouse path", "/sql/1.0/warehouses/<id>"],
        ["DATABRICKS_TOKEN", "Personal access token", "dapi***"],
        ["CATALOG", "Unity Catalog name", "aiagenticdemo"],
        ["SCHEMA_GOLD", "Gold schema name", "stars_gold"],
        ["SCHEMA_SILVER", "Silver schema name", "stars_silver"],
        ["SCHEMA_BRONZE", "Bronze schema name", "stars_bronze"],
        ["TWILIO_ACCOUNT_SID", "Twilio account", "AC***"],
        ["TWILIO_AUTH_TOKEN", "Twilio auth token", "***"],
        ["TWILIO_FROM_NUMBER", "SMS sender number", "+1***"],
        ["SENDGRID_API_KEY", "SendGrid API key", "SG.***"],
        ["SENDGRID_FROM_EMAIL", "Email sender address", "noreply@example.com"],
      ],
      [2800, 2800, 3760]
    ),
  ];
}

// ── ASSEMBLE DOCUMENT ────────────────────────────────────────────────────────
async function main() {
  const doc = new Document({
    styles: {
      default: { document: { run: { font: "Arial", size: 22 } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 36, bold: true, font: "Arial", color: BLUE },
          paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 28, bold: true, font: "Arial", color: BLUE },
          paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: "Arial", color: "333333" },
          paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
      ]
    },
    numbering: {
      config: [
        { reference: "bullets",
          levels: [
            { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
            { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
          ] },
      ]
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: ORANGE, space: 4 } },
            spacing: { after: 0 },
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
            children: [
              new TextRun({ text: "StarPulse Technical Design Document", size: 16, font: "Arial", color: "999999" }),
              new TextRun({ text: "\tv1.0 | Confidential", size: 16, font: "Arial", color: "999999" }),
            ]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC", space: 4 } },
            spacing: { before: 0 },
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
            children: [
              new TextRun({ text: "EXL Services | StarPulse Medicare Stars Platform", size: 16, font: "Arial", color: "999999" }),
              new TextRun({ text: "\tPage ", size: 16, font: "Arial", color: "999999" }),
              new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: "999999" }),
            ]
          })]
        })
      },
      children: [
        ...coverPage(),
        ...revisionHistory(),
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
        pageBreak(),
        ...section1(),
        ...section2(),
        ...section3(),
        ...section4(),
        ...section5(),
        ...section6(),
        ...section7(),
        ...section8(),
        ...section9(),
        ...section10(),
        ...section11(),
        ...section12(),
        ...section13(),
        ...section14(),
      ]
    }]
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync("C:\\STARS_FInal_Draft\\StarPulse_Technical_Design_Document.docx", buffer);
  console.log("Document generated: StarPulse_Technical_Design_Document.docx");
  console.log(`File size: ${(buffer.length / 1024).toFixed(0)} KB`);
}

main().catch(err => { console.error(err); process.exit(1); });
