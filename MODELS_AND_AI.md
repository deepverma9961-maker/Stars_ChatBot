# StarPulse — Models, AI, Features & Results

**Document scope.** This document inventories every model, scoring algorithm, agent, and generative-AI integration that exists in the StarPulse codebase as currently deployed at `https://stars-pulse-1356475297832733.aws.databricksapps.com`. It distinguishes between what is **actually implemented** in the live application versus what is **described as future-state** in the architecture documents that ship alongside the code.

---

## 0. Honest summary

The live StarPulse application is a **deterministic rules-and-heuristics engine** backed by Databricks SQL. As of this writing:

- **No ML libraries are imported** in any backend, frontend, or Databricks notebook file. There are zero references to `sklearn`, `xgboost`, `lightgbm`, `tensorflow`, `pytorch`, `prophet`, `mlflow`, or `pyspark.ml` anywhere in `stars-app/` or `stars_v2.html`.
- **No LLM / Gen-AI calls are made** at runtime. There are no imports of `openai`, `anthropic`, `langchain`, `transformers`, or `cohere`. No prompt strings, no `chat.completions` endpoints, no embeddings, no retrieval.
- The word **"agent"** in the codebase refers exclusively to the *UI workflow page* (`pg-agent`, the "Agent Execution" screen) where a human operator drives an outreach campaign week-by-week. It is not an autonomous LLM agent.
- The architecture artifacts `generate_arch_ml.js` and `generate_tdd.js` are Word/PDF generators that describe an **aspirational target state** (XGBoost propensity, Prophet/ARIMA forecasting, MLflow registry, LangChain + GPT-4 RAG). These describe what the platform *could* become; they do not exercise any model code.

Everything below documents what is *truly* in the running system, plus the planned ML/Gen-AI roadmap captured in the architecture docs.

---

## 1. Scoring algorithms in the live application

All projections, rate forecasts, member prioritisation, and channel/incentive recommendations are computed by deterministic formulas with hardcoded coefficients. Each one is listed below with its inputs, formula, location, and where the output appears in the UI.

### 1.1 Star rating calculator

**Location:** `stars-app/backend/services/star_calculator.py`

**Purpose:** Convert a measure-level numeric rate into a 1–5 star rating, then compute a weighted overall plan rating.

**Inputs (features):**
- `measure_code` (e.g. `HBD`, `CBP`, `SPC`)
- `current_rate` (percent, 0–100)
- A hardcoded `THRESHOLDS` table: per-measure 4-star cut, 5-star cut, and CMS weight.

**Formula (measure → stars):**
- `rate ≥ 5-star cut` → 5.0
- `rate ≥ 4-star cut` → 4.0
- `rate ≥ (4-star cut − 8)` → 3.0
- `rate ≥ (4-star cut − 16)` → 2.0
- otherwise → 1.0

**Formula (overall):**
```
overall = round_to_half( Σ(stars_i × weight_i) / Σ(weight_i) )
```

**Hardcoded thresholds (excerpt):**
| Measure | Weight | 4★ cut | 5★ cut |
|---|---|---|---|
| HBD (Diabetes BG) | 3× | 80 | 90 |
| CBP (BP Control) | 3× | 70 | 80 |
| PCR (Readmissions) | 3× | 75 | 85 |
| MRP (Med Review)  | 1× | 86 | 94 |

**Where it appears in the UI:** Executive page KPIs, Plan Detail page star summary, Star Summary endpoint (`/api/star-summary`).

### 1.2 Simulator engine — closure-rate and lift projection

**Location:** Frontend `stars_v2.html` (`calcSimResult()` around line 2860), backend `stars-app/backend/services/simulator_engine.py`.

**Purpose:** Given a target HEDIS / CAHPS / Adherence measure and the user's selected gap/propensity/EHO filter chips, project how many gaps will close, how much the rate lifts, and what the projection looks like over a 4-week waterfall.

**Inputs (features):**
- Measure metadata: `gaps`, `pct` (current rate), `code`
- User-selected filter buckets: `gap_status ∈ {Open, Partial, Borderline}`, `propensity_tier ∈ {high, medium, low}`, `eho_segment`
- Per-channel base closure rate, per-incentive boost (constants below)

**Formula (closure rate):**
```
closureRate(channel, incentive)
  = base[channel] + boost[incentive]
  base    = { Call: 0.28, SMS: 0.22, Email: 0.12 }
  boost   = { None: 0.00, '$25 card': 0.04, '$50 card': 0.08 }
```
Max achievable closure rate = 0.40 (Call + $50 card).

**Formula (eligible denominator):**
```
eligible = round( gaps / max(0.02, 1 − pct/100) )
```
The `0.02` floor caps a 99% performer at a 50× pool inflation (this floor was tightened from `0.01` in a recent fix).

**Formula (projection):**
```
matched   = gap_total × propensity_weight × eho_weight
net_pool  = max(0, matched − suppressions)
te        = Σ over segments ( segment_count × closure_rate )
lift_pp   = (te / eligible) × 100
projected = min(100, pct + lift_pp)
```

**Channel and incentive auto-assignment (heuristics):**
```
autoChannel(prop, gap)   = high|open  → Call
                           medium|partial → SMS
                           low|borderline → Email
autoIncentive(prop, gap) = open,high   → None
                           open,medium → $25 card
                           partial     → $25 card
                           borderline  → $50 card
```

**Auto-fill-to-cut (added recently):** when the projected rate falls below the per-measure 4★ cut, the simulator turns on every gap/prop/EHO chip, recomputes, and either lands at or above the cut, or reports `"Max achievable X.X% — pool is N gaps short of the YY% cut even with maximal outreach."`

**Per-measure 4★ cuts wired into the simulator:**
- `HEDIS_CUTS` (14 measures): HBD 79, CBP 80, PCR 75, BCS 75, COL 71, COA_MR 86, COA_PA 92, OMW 63, EED 79, KED 81, MRP 85, SPC 88, TRC 65, AMM 70.
- `ADH_CUTS` (6 measures): PDC-DR 88, PDC-RAS 86, PDC-STA 86, MTM 70, MPR 80, SPC-ADH 87.

**Waterfall weekly distribution:** `[0.40, 0.30, 0.20, 0.10]` — fixed; not learned.

**Cost per closure:**
```
cost = base[channel] + cost[incentive]
base = { Call: $22, SMS: $4, Email: $2 }
cost = { None: 0, $25 card: 25, $50 card: 50 }
```

**Where it appears in the UI:** Simulator page — current/projected KPIs, segment table, waterfall, member pool table, risk score chip.

### 1.3 Risk score

**Location:** `stars_v2.html:2895-2913` (`calcRiskScore`)

**Formula:**
```
raw = (high_open / matched × 0.55)
    + (med_partial / matched × 0.25)
    − (suppressed / matched × 0.20)
score = clamp(0, 100, round(raw × 100))
```
Buckets: `< 40` High Risk, `40–69` Moderate, `≥ 70` Low Risk.

**Where it appears in the UI:** Simulator → Risk chip on the auto/HIL mode KPI strip.

### 1.4 HOS urgency factors (schema only)

**Location:** `stars-app/backend/routers/hos.py` → `_MEASURES["fall"]["urgency_factors"]`

The seven factors and their weights are *displayed* on the HOS Urgency Engine page:
| Factor | Weight |
|---|---|
| Fall history severity | 25 |
| AWV status | 20 |
| Age | 15 |
| Comorbidities | 15 |
| Mock survey response | 10 |
| Time since last visit | 10 |
| Homebound status | 5 |

**Important honesty note:** these weights are presented as a scoring framework in the UI, but the actual `urgency_score` assigned to each member in the fallback path is `rng.randint(15, 98)` (line 147 of `hos.py`) — a uniform random draw. When the live Databricks table `gold_hos_members.urgency_score` is available, the API returns the value stored there; the *production computation* of that column would be the responsibility of the data team and is not implemented in this repo.

### 1.5 Member propensity / channel routing in the data layer

**Location:** `stars-app/notebooks/gold/11_gold_member_gaps.py` (PySpark notebook)

The notebook materialises `aiagenticdemo.stars_gold.gold_member_gap` with a per-member `propensity_score` and a `recommended_channel` / `recommended_incentive`. The current implementation uses:
```python
propensity = round(r.uniform(20, 95), 1)
gap_status = r.choices(['Open','Partial','Borderline'], weights=[55, 30, 15])[0]

if   propensity > 75: channel = 'Call'
elif propensity > 40: channel = 'SMS'
else:                 channel = 'Email'

if   propensity > 80: incentive = 'None'
elif propensity > 60: incentive = '$25 card'
else:                 incentive = '$50 card'
```
The propensity is therefore a uniform random draw used to drive deterministic threshold routing — not a learned probability. The thresholds (75 / 40, 80 / 60) match the simulator's `autoChannel` / `autoIncentive` heuristics.

---

## 2. Databricks data flow (bronze → silver → gold)

The Databricks layer is built by 14 PySpark notebooks under `stars-app/notebooks/`. None of them import any ML library; all "scores" emitted by the gold layer are random draws or deterministic threshold rules over those random draws. The pipeline is intended as the seam where a future predictive model would plug in.

| Layer | Notebook | What it builds | ML/AI content |
|---|---|---|---|
| Bronze | `01_bronze_enrollment.py` | Raw enrollment + demographics (PII) | None |
| Bronze | `02_bronze_claims.py` | Raw claims facts | None |
| Bronze | `03_bronze_pharmacy.py` | Raw pharmacy fills (PDC source) | None |
| Bronze | `04_bronze_cahps.py` | Raw CAHPS survey responses | None |
| Bronze | `05_bronze_call_center.py` | Raw call-center interactions | None |
| Silver | `06_silver_member_plan.py` | Cleaned member + plan, PII hashed, `utilization_segment` assigned | None |
| Silver | `07_silver_measure_cahps.py` | Measure definitions, CAHPS composites | None |
| Silver | `08_silver_clinical_events.py` | Diagnoses + procedures, ICD-10 grouped | None |
| Gold | `09_gold_star_ratings.py` | `gold_star_rating_summary` — overall ratings per contract | Hardcoded baseline + small noise |
| Gold | `10_gold_measure_scorecard.py` | `gold_measure_scorecard` — per-measure per-plan rates | Hardcoded baseline + small noise |
| Gold | `11_gold_member_gaps.py` | `gold_member_gap` — member × measure registry with `propensity_score`, `recommended_channel`, `recommended_incentive` | Random propensity + threshold rules (see §1.5) |
| Gold | `12_gold_cahps_teamview.py` | `gold_team_view` — department-level CAHPS attribution | None |
| Gold | `13_gold_campaigns_alerts.py` | `gold_campaign`, `gold_alert` | None |
| Gold | `14_gold_hos.py` | `gold_hos_measures`, `gold_hos_scorecard`, `gold_hos_members`, `gold_hos_provider_scorecard` — HOS measure data with `urgency_score` | Random urgency draw + threshold rules (see §1.4) |

**What the gold tables expose to the application:** rates, gap counts, member rosters, provider rosters, propensity / urgency scores, recommended channel + incentive. The FastAPI backend queries these tables (`stars-app/backend/db.py`) and falls back to the in-process mock generators in `routers/hos.py` and `services/simulator_engine.py` when Databricks is unreachable.

---

## 3. Agents and Gen-AI in the live app

| Reference | What it is in code | Is it actually agentic / Gen-AI? |
|---|---|---|
| "Agent Execution" sidebar tab → `pg-agent` page | A UI workflow: pick week → see member list → click "Call / SMS / Email" → log outcome. Templates and scripts are static strings. | **No.** It is a human-driven outreach console. The "agent" is the *call-center agent* (person), not an LLM. |
| "Agent Queue" / "Agent scripts" labels | Static lookup tables: gap-status → script string | **No.** No generation, no reasoning. |
| HOS "Urgency Engine" narrative banner | UI copy describing how scores *would* be computed; the score itself comes from the gold table or the random fallback | **No** runtime AI. |
| Alerts page "Agent assist copilot" tile | A *recommendation card* describing a possible future intervention; clicking it opens a static suggestion modal | **No** runtime AI. |
| Outreach service (`outreach_service.py`) | Wraps Twilio (SMS) and SendGrid (email) — message body comes from a static template with variable interpolation (`[member_name]`, `[measure]`) | **No.** Provider integration only, no LLM call. |

**Summary:** the running platform has neither an autonomous agent nor any call into a generative model.

---

## 4. Planned (aspirational) ML + Gen-AI stack

Two scripts in the repo root generate Word documents that describe a *target architecture* for a future production release:

- `generate_arch_ml.js` — generates the ML architecture doc.
- `generate_tdd.js` — generates the technical design doc.

These documents describe the following components, which are **not implemented in the application code**:

| Component | Doc reference | Status |
|---|---|---|
| Member-level closure-probability model | `generate_arch_ml.js:285`, `generate_tdd.js:1011` — "XGBoost gradient-boosted classifier" | Aspirational |
| Time-series rate forecast | `generate_arch_ml.js:301`, `generate_tdd.js:1027` — "Prophet (seasonal decomposition) + ARIMA (short-term trend)" | Aspirational |
| Model registry / lifecycle | `generate_arch_ml.js:327`, `generate_tdd.js:1056` — MLflow with hyperparameter logging, AUC / precision / recall | Aspirational |
| Gen-AI summarisation / member narrative | `generate_tdd.js:1116, 1148` — "LangChain prompt chains" + "GPT-4" + retrieval index | Aspirational |
| Replacement of static `closure_rate` dict | `generate_arch_ml.js:453` — "Replace static closure_rate dict with per-member XGBoost predictions" | Aspirational |
| Replacement of static rate projection | `generate_arch_ml.js:457` — "Prophet seasonal decomposition + ARIMA short-term trend with confidence intervals" | Aspirational |

These items are useful as a roadmap, but they should not be presented to stakeholders as features of the *current* product.

---

## 5. Features and parameters by component (consolidated)

| Component | Inputs (features) | Tunable parameters | Where features come from |
|---|---|---|---|
| Star calculator | `measure_code`, `current_rate` | `THRESHOLDS[measure_code]`: 4★, 5★, weight | `gold_measure_scorecard` |
| Simulator closure-rate | `channel`, `incentive` | `CLOSURE_RATES`, `INCENTIVE_BOOST`, `COST_BASE`, `INCENTIVE_COST` | User-selected UI chips |
| Simulator projection | `gaps`, `pct`, gap-status mix, propensity mix, EHO mix, suppression counts | `GAP_WEIGHT 0.55/0.30/0.15`, `PROP_WEIGHT 0.25/0.42/0.33`, `WATERFALL_DIST 0.4/0.3/0.2/0.1`, eligible floor `0.02` | Measure metadata + UI filters |
| Simulator risk score | `high_open`, `med_partial`, `matched`, `suppressed` | Coefficients `0.55 / 0.25 / 0.20` | Same filter selection |
| Per-measure 4★ cut | `measure_code` | `HEDIS_CUTS`, `ADH_CUTS` lookup tables | Hardcoded from CMS published cuts |
| Auto-fill-to-cut | Per-measure cut, current rate, gaps, max closure rate `0.40` | Same constants as above | Same |
| HOS urgency factors | (display only) age, AWV, comorbidities, mock survey, time since visit, fall severity, homebound | Weights 25 / 20 / 15 / 15 / 10 / 10 / 5 | UI-only schema |
| HOS urgency score (runtime) | None — random uniform `[15, 98]` in fallback; gold-table value otherwise | n/a | `gold_hos_members.urgency_score` |
| Member propensity (gold notebook) | None — random uniform `[20, 95]` | Channel/incentive thresholds 75/40 and 80/60 | `gold_member_gap.propensity_score` |
| Outreach service | Member ID, channel, template | Twilio / SendGrid API keys; template strings | Static templates |

---

## 6. Results we actually produce

Because nothing in the system is trained, "model accuracy" metrics do not apply. The system's *outputs* are deterministic functions of inputs, and the user-visible results are:

| Surface | Result |
|---|---|
| Executive page | Plan-level star rating, gap totals, projected QBP at stake — all derived from `gold_star_rating_summary` + the star calculator. |
| Plan Detail page | Per-domain rates, measure-level breakdown — read from `gold_measure_scorecard`. |
| Simulator | A projected lift and a 4-week waterfall for any combination of measure + channel mix + incentive mix. Maximum achievable lift is structurally bounded by `0.40 × (1 − pct/100) × 100`. After the recent auto-fill-to-cut fix, every measure now lands at-or-above its 4★ cut whenever the pool allows; otherwise the UI displays the structural ceiling explicitly. |
| HOS page | 5-measure overview with rate / gap / AWV badges; per-measure deep-dive with Survey & Scores / Outreach Campaigns / PCP Outreach / Care Management tabs. |
| CAHPS page | Composite scores, pulse-survey waves, team-view interventions — rendered instantly with fallback data, refreshed when `/api/cahps` returns. |
| Medical Adherence page | 6-measure roster, each row clicks through to the simulator with the right measure and 4★ cut pre-loaded. |
| Outreach actions | Twilio SMS and SendGrid emails are sent for real when API keys are configured. Templates substitute member-name / measure variables only. |

There are no precision, recall, AUC, MAPE, or BLEU figures to report — the relevant metrics for the current system are operational (latency, uptime, fallback hit-rate), not model-quality.

---

## 7. Why this approach was used

- **Time-to-stakeholder-demo.** A deterministic rules engine over Databricks tables gave the team a fully working dashboard with realistic interactions in days, without the dataset preparation, labelling, training, validation, monitoring, and governance overhead that a real model would require.
- **Transparent reasoning.** Every projection in the UI is a one-line formula a reviewer can follow. There is no "black box" to defend in a CMS audit context.
- **Architecture-ready.** The Databricks bronze→silver→gold layout, the `gold_member_gap.propensity_score` column, and the `services/simulator_engine.py` seam are all positioned so a future model can replace specific scores without changing the UI contract.
- **Honest cost profile.** No inference cost, no LLM-token cost, no model-serving infrastructure.

The trade-off: any "AI" framing should be treated as future-state, not current-state.

---

## 8. Recommended next steps to genuinely add ML / Gen-AI

If the team wants to convert the aspirational architecture in `generate_arch_ml.js` / `generate_tdd.js` into a live product, the lowest-friction sequence is:

1. **Replace `propensity_score` in `gold_member_gap`** with a real XGBoost / LightGBM classifier trained on historical outreach outcomes. The classifier's features (claims recency, AWV history, prior-channel response, demographics) already exist in silver. Wrap it as a Databricks Model Serving endpoint; have the gold notebook write the model's probability into the same column. No frontend or API change needed.
2. **Replace `closureRate(channel, incentive)`** with a per-member, per-channel probability — same model output, evaluated for the candidate channel.
3. **Replace the random `urgency_score`** in `gold_hos_members` with a real score from a model that consumes the seven factors already documented in the HOS UI.
4. **Add Prophet / ARIMA** as a Databricks job that writes `projected_rate_year_end` for each measure into a new gold column. The Simulator's "projected" line can then carry a confidence band.
5. **Introduce GPT-4 / Claude** behind a single FastAPI route (`/api/ai/explain?context=...`) for *narrative* outputs only (e.g. summarising a HOS member's urgency factors, drafting a PCP-email body). Keep the deterministic numerics; let the LLM produce prose. This is the cheapest meaningful Gen-AI footprint.
6. **Stand up MLflow** in the Databricks workspace and register every model from step 1–4 there. Wire `connection-status` to surface model-version metadata alongside the data-source freshness it already shows.

Each of these is independently shippable and does not require rewriting the front end.

---

## 9. Document provenance

- Audit performed by reading every file under `stars-app/backend/`, `stars-app/notebooks/`, `stars-app/backend/queries/`, and the JS within `stars_v2.html`.
- Search terms used to confirm absence of ML / Gen-AI: `sklearn`, `xgboost`, `lightgbm`, `tensorflow`, `pytorch`, `prophet`, `mlflow`, `pyspark.ml`, `openai`, `anthropic`, `langchain`, `transformers`, `cohere`, `gpt`, `claude`, `gemini`, `llama`.
- All formulas quoted in §1 are copied verbatim from the cited file lines.
- All "aspirational" references in §4 are direct line citations from the doc-generator scripts; those scripts produce Word docs, they do not exercise model code.
