# CLAUDE.md — StarPulse Medicare Stars Platform

## Project Overview

StarPulse is an AI-powered Medicare Stars management dashboard built for EXL Services. It tracks HEDIS gaps, CAHPS scores, member outreach, and CMS star ratings across health plan contracts.

**Live app:** `https://stars-pulse-1356475297832733.aws.databricksapps.com`
**Databricks profile:** `stars`
**Workspace path:** `/Workspace/stars-app`
**App name:** `stars-pulse`

---

## Architecture

```
STARS_FInal_Draft/
├── stars_v2.html              ← PRIMARY FRONTEND (self-contained, served as dist/index.html)
├── fix_html_v4.py             ← Utility script for patching stars_v2.html programmatically
├── stars-app/
│   ├── app.yaml               ← Databricks App config (uvicorn command + env vars)
│   ├── requirements.txt       ← Python deps
│   ├── deploy.sh              ← Full deploy script (has Windows path-spacing bug — use PowerShell instead)
│   ├── backend/               ← FastAPI backend
│   │   ├── main.py            ← App entry point, serves frontend/dist/index.html for all non-API routes
│   │   ├── config.py          ← Pydantic settings (reads DATABRICKS_* env vars)
│   │   ├── db.py              ← Databricks SQL connector
│   │   ├── routers/           ← API route handlers (plans, hedis, cahps, members, etc.)
│   │   ├── models/            ← Pydantic response models
│   │   └── services/          ← Business logic (simulator engine, star calculator)
│   └── frontend/
│       ├── dist/index.html    ← Deployed frontend (copy of stars_v2.html)
│       └── src/               ← React app (NOT currently served — stars_v2.html is used instead)
```

---

## Frontend — stars_v2.html

The live frontend is `stars_v2.html` — a **single self-contained HTML file** with all CSS and JS inline. No build step required.

### Pages (nav order matches stars_v2.html)
| Nav Label | Page ID | Description |
|---|---|---|
| Marketing Overview | `marketing` | Hero + capability cards (no sidebar) |
| Executive | `executive` | KPI cards + plan table with filters |
| Plan Detail | `plan` | Per-contract ratings, domains, HEDIS/CAHPS breakdown |
| HEDIS Measures | `hedis` | Measure-level gap analysis |
| Simulator | `simulator` | Star rating scenario modeler |
| Agent Execution | `agent` | Outreach campaign execution |
| Impact Projector | `impact` | Closure rate simulator |
| Campaign History & ROI | `roi` | Campaign tracking and ROI |
| Alerts & Priorities | `alerts` | Critical alerts and action items |
| Member Gap List | `member-gap-list` | Member-level gap registry |
| CAHPS Overview | `cahps` | CAHPS survey monitoring |

### Key CSS classes
- `.app.marketing-mode .topbar { display:none }` — hides sidebar on marketing page
- `.cap-card::before` — orange top accent bar on capability cards
- `.cap-link` — "Explore →" / "Launch →" link color
- `.ntab.active` — active nav item style (left border + bg)

### Brand Colors
- **EXL Orange:** `#F26722` (primary accent — headlines, links, borders, logo)
- **Active nav / alerts:** `#c0392b` (red — keep for status indicators only)
- **Hero background:** `linear-gradient(135deg,#1a1a2e 0%,#2d1b1b 60%,#3d1a1a 100%)`

### Marketing Page Rules
- Sidebar is hidden (`.app.marketing-mode .topbar { display:none }`)
- EXL logo shown in hero: `EXL | StarPulse · Medicare Stars Platform`
- No icons on capability cards (`.cap-icon` divs removed)
- No icon on Executive Overview card

---

## Backend — FastAPI

**Entry point:** `backend/main.py`
**Base URL for all API routes:** `/api`

### Key Endpoints
| Endpoint | Description |
|---|---|
| `GET /api/connection-status` | Checks Databricks live connection |
| `GET /api/star-summary` | Portfolio-level KPIs |
| `GET /api/plans` | All plan summaries (supports filters) |
| `GET /api/plans/{contract_id}` | Single plan detail |
| `GET /api/hedis-measures` | HEDIS measure data |
| `GET /api/cahps` | CAHPS survey scores |
| `GET /api/members/gaps` | Member gap list |
| `GET /api/campaigns` | Campaign history |
| `GET /api/alerts` | Alerts and priorities |
| `GET /api/team-view` | Team accountability view |

**Data:** Falls back to static/faker-generated data when Databricks is unreachable. The frontend shows "STATIC DATA" or "LIVE DATA" badge accordingly.

### Databricks config (app.yaml env vars)
- `DATABRICKS_HOST` — workspace URL
- `DATABRICKS_HTTP_PATH` — SQL warehouse path
- `DATABRICKS_TOKEN` — PAT token
- `CATALOG` — `aiagenticdemo`
- `SCHEMA_GOLD` — `stars_gold`
- `SCHEMA_SILVER` — `stars_silver`
- `SCHEMA_BRONZE` — `stars_bronze`

---

## Deployment

### How to deploy (Windows — use PowerShell, NOT deploy.sh)
`deploy.sh` has a bug on Windows: the Databricks CLI path contains spaces (`Aman Deep  Verma`) which breaks the old Python CLI's auto-detection. Always use the new CLI directly via PowerShell.

```powershell
$cli = "C:\Users\Aman Deep  Verma\AppData\Local\Microsoft\WinGet\Packages\Databricks.DatabricksCLI_Microsoft.Winget.Source_8wekyb3d8bbwe\databricks.exe"
$profile = "stars"

# 1. Upload frontend (after editing stars_v2.html, copy it to dist first)
cp C:\STARS_FInal_Draft\stars_v2.html C:\STARS_FInal_Draft\stars-app\frontend\dist\index.html
& $cli workspace import "/Workspace/stars-app/frontend/dist/index.html" `
    --file "C:\STARS_FInal_Draft\stars-app\frontend\dist\index.html" `
    --format RAW --overwrite --profile $profile

# 2. (If backend changed) Upload backend
& $cli workspace import-dir "C:\STARS_FInal_Draft\stars-app\backend" `
    "/Workspace/stars-app/backend" --overwrite --profile $profile

# 3. Redeploy app
& $cli apps deploy "stars-pulse" --source-code-path "/Workspace/stars-app" --profile $profile
```

### Frontend-only change (most common)
Edit `stars_v2.html` → copy to `dist/index.html` → upload index.html → redeploy. No build step needed.

### React app (NOT currently served)
The React app in `stars-app/frontend/src/` is not used. If ever needed:
- Requires `postcss.config.js` to exist (was missing — caused Tailwind not to compile)
- Build: `npm run build` from `stars-app/frontend/`
- Then upload `frontend/dist/` directory instead of just `index.html`

---

## React App Notes (archived)

The React app was previously the frontend but was replaced by `stars_v2.html` due to CSS compilation issues. Key lessons:

- **postcss.config.js was missing** — Tailwind directives (`@tailwind`, `@apply`) were written as raw text into the CSS output, so no utility classes worked. Fixed by creating the file, but then switched to HTML approach.
- **Tailwind purging** — Classes only used in new files (e.g., `bg-white`) got purged if not in original build. Use inline styles for new layout-heavy pages.
- **Databricks CLI path spacing** — Windows username `Aman Deep  Verma` breaks the old Python CLI. Always use the WinGet-installed CLI via quoted path.

---

## Key Files to Edit

| Task | File |
|---|---|
| Change marketing page layout/content | `stars_v2.html` (lines ~263–294) |
| Change marketing page CSS | `stars_v2.html` (lines ~125–139) |
| Change sidebar nav | `stars_v2.html` (lines ~243–255) |
| Add/change API endpoint | `stars-app/backend/routers/*.py` |
| Change Databricks queries | `stars-app/backend/routers/*.py` or `queries/*.sql` |
| Change app config/env | `stars-app/app.yaml` |
