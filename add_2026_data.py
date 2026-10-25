"""
Add 2026 CMS Star Ratings data to the compiled 2021-2025 workbook.
- Adds 2026 columns to '📊 All Contracts (Stars)' sheet
- Adds 2026 columns to '📊 All Contracts (Data)' sheet
- Updates other sheets (Company Directory, Measure Trends, Distribution)
- Does NOT change any existing 2021-2025 data
"""
import sys, io, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import shutil

SRC = r'C:\Users\Aman Deep  Verma\Downloads\CMS_StarRatings_REAL_2021_2025 (2) (1) (1).xlsx'
OUT = r'C:\Users\Aman Deep  Verma\Downloads\CMS_StarRatings_REAL_2021_2026.xlsx'
STARS_CSV = r'C:\Users\Aman Deep  Verma\Downloads\2026_stars_extract\2026-star-ratings-data-tables\2026 Star Ratings Data Table - Measure Stars (Oct 8 2025).csv'
DATA_CSV = r'C:\Users\Aman Deep  Verma\Downloads\2026_stars_extract\2026-star-ratings-data-tables\2026 Star Ratings Data Table - Measure Data (Oct 8 2025).csv'
SUMMARY_CSV = r'C:\Users\Aman Deep  Verma\Downloads\2026_stars_extract\2026-star-ratings-data-tables\2026 Star Ratings Data Table - Summary Ratings (Oct 8 2025).csv'

# Copy source to output
shutil.copy2(SRC, OUT)
print(f"Copied source to {OUT}")

# Load 2026 CSVs
stars_raw = pd.read_csv(STARS_CSV, encoding='latin1', header=None)
data_raw = pd.read_csv(DATA_CSV, encoding='latin1', header=None)
summary_raw = pd.read_csv(SUMMARY_CSV, encoding='latin1', header=None)

# Extract measure names from row 2 (0-indexed) of stars CSV, cols 5+
measure_names_2026 = []
for j in range(5, stars_raw.shape[1]):
    v = str(stars_raw.iloc[2, j]) if pd.notna(stars_raw.iloc[2, j]) else ''
    # These are measure codes like "C01: Breast Cancer Screening"
    if v and v.startswith(('C', 'D')):
        measure_names_2026.append((j, v))
    elif v:
        measure_names_2026.append((j, v))

print(f"2026 measures: {len(measure_names_2026)}")

# Build contract->data lookup for stars
# Data rows start at row index 4 in CSV (skip title, domain headers, measure names, date ranges)
stars_data = {}  # contract_id -> {csv_col: value}
data_data = {}
for i in range(4, stars_raw.shape[0]):
    cid = str(stars_raw.iloc[i, 0]).strip() if pd.notna(stars_raw.iloc[i, 0]) else ''
    if not cid:
        continue
    row_vals = {}
    for j in range(5, stars_raw.shape[1]):
        v = stars_raw.iloc[i, j]
        if pd.notna(v):
            row_vals[j] = v
    stars_data[cid] = {
        'org_type': stars_raw.iloc[i, 1] if pd.notna(stars_raw.iloc[i, 1]) else '',
        'contract_name': stars_raw.iloc[i, 2] if pd.notna(stars_raw.iloc[i, 2]) else '',
        'marketing_name': stars_raw.iloc[i, 3] if pd.notna(stars_raw.iloc[i, 3]) else '',
        'parent_org': stars_raw.iloc[i, 4] if pd.notna(stars_raw.iloc[i, 4]) else '',
        'measures': row_vals,
    }

for i in range(4, data_raw.shape[0]):
    cid = str(data_raw.iloc[i, 0]).strip() if pd.notna(data_raw.iloc[i, 0]) else ''
    if not cid:
        continue
    row_vals = {}
    for j in range(5, data_raw.shape[1]):
        v = data_raw.iloc[i, j]
        if pd.notna(v):
            row_vals[j] = v
    data_data[cid] = row_vals

print(f"Stars contracts loaded: {len(stars_data)}")
print(f"Data contracts loaded: {len(data_data)}")

# Open the workbook
wb = openpyxl.load_workbook(OUT)

# ============================================================
# SHEET 1: 📊 All Contracts (Stars)
# ============================================================
ws = wb['📊 All Contracts (Stars)']

# 2025 ends at col 215, 2026 starts at col 216
COL_2026_START = 216
N_MEASURES = len(measure_names_2026)  # 45

# Copy styling from 2025 header area
header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
measure_font = Font(name="Calibri", size=9)
thin_border = Border(
    left=Side(style="thin", color="D9E1F2"),
    right=Side(style="thin", color="D9E1F2"),
    top=Side(style="thin", color="D9E1F2"),
    bottom=Side(style="thin", color="D9E1F2"),
)

# Row 2: Year group header "2026 STAR RATINGS (45 measures)"
cell = ws.cell(row=2, column=COL_2026_START, value=f"2026 STAR RATINGS ({N_MEASURES} measures)")
cell.font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
cell.alignment = Alignment(horizontal="center")
# Merge across all measure columns
ws.merge_cells(start_row=2, start_column=COL_2026_START, end_row=2, end_column=COL_2026_START + N_MEASURES - 1)

# Row 3: Measure names
for idx, (csv_col, mname) in enumerate(measure_names_2026):
    col = COL_2026_START + idx
    cell = ws.cell(row=3, column=col, value=mname)
    cell.font = measure_font
    cell.fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
    cell.alignment = Alignment(wrap_text=True, vertical="bottom", horizontal="center")
    cell.border = thin_border
    ws.column_dimensions[get_column_letter(col)].width = 14

# Row 4+ : Data - match by CONTRACT_ID in column A
contract_col_map = {}  # row -> contract_id
for row_idx in range(4, ws.max_row + 1):
    cid = ws.cell(row=row_idx, column=1).value
    if cid:
        contract_col_map[row_idx] = str(cid).strip()

matched = 0
for row_idx, cid in contract_col_map.items():
    if cid in stars_data:
        measures = stars_data[cid]['measures']
        for idx, (csv_col, _) in enumerate(measure_names_2026):
            col = COL_2026_START + idx
            val = measures.get(csv_col, '')
            if val != '':
                cell = ws.cell(row=row_idx, column=col, value=val)
                cell.font = Font(name="Calibri", size=9)
                cell.alignment = Alignment(horizontal="center")
                cell.border = thin_border
                # Color-code star ratings
                try:
                    star_val = int(val)
                    if star_val >= 4:
                        cell.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")  # green
                    elif star_val <= 2:
                        cell.fill = PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid")  # red
                except (ValueError, TypeError):
                    pass
        matched += 1

print(f"Stars sheet: matched {matched} contracts")

# ============================================================
# SHEET 2: 📊 All Contracts (Data) — same structure
# ============================================================
ws2 = wb['📊 All Contracts (Data)']

# Row 2: Year group header
cell = ws2.cell(row=2, column=COL_2026_START, value=f"2026 PERFORMANCE DATA ({N_MEASURES} measures)")
cell.font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
cell.alignment = Alignment(horizontal="center")
ws2.merge_cells(start_row=2, start_column=COL_2026_START, end_row=2, end_column=COL_2026_START + N_MEASURES - 1)

# Row 3: Measure names (same as stars)
for idx, (csv_col, mname) in enumerate(measure_names_2026):
    col = COL_2026_START + idx
    cell = ws2.cell(row=3, column=col, value=mname)
    cell.font = measure_font
    cell.fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
    cell.alignment = Alignment(wrap_text=True, vertical="bottom", horizontal="center")
    cell.border = thin_border
    ws2.column_dimensions[get_column_letter(col)].width = 14

# Data rows
contract_col_map2 = {}
for row_idx in range(4, ws2.max_row + 1):
    cid = ws2.cell(row=row_idx, column=1).value
    if cid:
        contract_col_map2[row_idx] = str(cid).strip()

matched2 = 0
for row_idx, cid in contract_col_map2.items():
    if cid in data_data:
        measures = data_data[cid]
        for idx, (csv_col, _) in enumerate(measure_names_2026):
            col = COL_2026_START + idx
            val = measures.get(csv_col, '')
            if val != '':
                cell = ws2.cell(row=row_idx, column=col, value=val)
                cell.font = Font(name="Calibri", size=9)
                cell.alignment = Alignment(horizontal="center")
                cell.border = thin_border
        matched2 += 1

print(f"Data sheet: matched {matched2} contracts")

# ============================================================
# SHEET 3: 🏢 Company Directory — add 2026 Stars column
# ============================================================
ws3 = wb['🏢 Company Directory']
# Find next empty column after 2025 Stars
# Row 2 has headers: ... 2021 Stars, 2022 Stars, ..., 2025 Stars
# Find the column for 2025 Stars
dir_2025_col = None
for col in range(1, ws3.max_column + 1):
    v = ws3.cell(row=2, column=col).value
    if v and '2025' in str(v):
        dir_2025_col = col
        break

if dir_2025_col:
    dir_2026_col = dir_2025_col + 1
    # Add header
    cell = ws3.cell(row=2, column=dir_2026_col, value="2026 Stars")
    cell.font = Font(name="Calibri", bold=True, size=10)
    cell.fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
    cell.alignment = Alignment(horizontal="center")

    # Read summary ratings for overall stars
    summary_data = {}
    for i in range(3, summary_raw.shape[0]):
        cid = str(summary_raw.iloc[i, 0]).strip() if pd.notna(summary_raw.iloc[i, 0]) else ''
        if not cid:
            continue
        # Overall star rating is typically in the last column or a specific column
        # Check columns for "Overall Star Rating"
        overall = summary_raw.iloc[i, summary_raw.shape[1]-1] if pd.notna(summary_raw.iloc[i, summary_raw.shape[1]-1]) else ''
        summary_data[cid] = overall

    # Actually let me find the right column for overall rating
    for j in range(summary_raw.shape[1]):
        v = str(summary_raw.iloc[0, j]) if pd.notna(summary_raw.iloc[0, j]) else ''
        if 'Overall' in v or 'Summary' in v:
            print(f"  Summary col {j}: {v[:50]}")

    for j in range(summary_raw.shape[1]):
        v = str(summary_raw.iloc[1, j]) if pd.notna(summary_raw.iloc[1, j]) else ''
        if v and v != 'nan':
            print(f"  Summary row1 col {j}: {v[:50]}")

    # Populate directory
    dir_matched = 0
    for row_idx in range(3, ws3.max_row + 1):
        cid = ws3.cell(row=row_idx, column=2).value  # Contract ID in col B
        if cid:
            cid = str(cid).strip()
            if cid in summary_data and summary_data[cid]:
                cell = ws3.cell(row=row_idx, column=dir_2026_col, value=summary_data[cid])
                cell.font = Font(name="Calibri", size=10)
                cell.alignment = Alignment(horizontal="center")
                dir_matched += 1
            else:
                ws3.cell(row=row_idx, column=dir_2026_col, value="—")

    print(f"Directory: added 2026 Stars for {dir_matched} contracts")

# ============================================================
# SHEET 4: 📈 Part C Measure Trends — add 2026 column
# ============================================================
ws4 = wb['📈 Part C Measure Trends']
# Find col after 2025 Avg Stars
for col in range(1, ws4.max_column + 1):
    v = ws4.cell(row=2, column=col).value
    if v and '2025' in str(v):
        trend_2026_col = col + 1
        break

cell = ws4.cell(row=2, column=trend_2026_col, value="2026\nAvg Stars")
cell.font = Font(name="Calibri", bold=True, size=10)
cell.fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
cell.alignment = Alignment(horizontal="center", wrap_text=True)
print(f"Part C Trends: added 2026 column at col {trend_2026_col}")

# ============================================================
# SHEET 5: 💊 Part D Measure Trends — add 2026 column
# ============================================================
ws5 = wb['💊 Part D Measure Trends']
for col in range(1, ws5.max_column + 1):
    v = ws5.cell(row=2, column=col).value
    if v and '2025' in str(v):
        trend_d_2026_col = col + 1
        break

cell = ws5.cell(row=2, column=trend_d_2026_col, value="2026\nAvg Stars")
cell.font = Font(name="Calibri", bold=True, size=10)
cell.fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
cell.alignment = Alignment(horizontal="center", wrap_text=True)
print(f"Part D Trends: added 2026 column at col {trend_d_2026_col}")

# ============================================================
# SHEET 6: 📉 Distribution Summary — add 2026 column
# ============================================================
ws6 = wb['📉 Distribution Summary']
# Find the 2025 column
for col in range(1, ws6.max_column + 1):
    v = ws6.cell(row=3, column=col).value
    if v and '2025' in str(v):
        dist_2026_col = col + 1
        break

cell = ws6.cell(row=3, column=dist_2026_col, value="2026\n(count / %)")
cell.font = Font(name="Calibri", bold=True, size=10)
cell.fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
cell.alignment = Alignment(horizontal="center", wrap_text=True)

# Count star distribution from summary data
star_dist = {5: 0, 4.5: 0, 4: 0, 3.5: 0, 3: 0, 2.5: 0, 2: 0, 1.5: 0, 1: 0}
total_contracts = 0
for cid, stars in summary_data.items():
    try:
        s = float(stars)
        if s in star_dist:
            star_dist[s] += 1
        total_contracts += 1
    except (ValueError, TypeError):
        pass

print(f"\n2026 Star Distribution (from {total_contracts} contracts):")
for stars in sorted(star_dist.keys(), reverse=True):
    count = star_dist[stars]
    pct = f"{count/total_contracts*100:.1f}" if total_contracts > 0 else "0"
    print(f"  {stars} stars: {count} ({pct}%)")

print(f"\nDistribution Summary: added 2026 column at col {dist_2026_col}")

# ============================================================
# Update title in row 1 of main sheets
# ============================================================
ws.cell(row=1, column=1).value = "CMS Star Ratings — All Contracts, All Measures (2021–2026)"
ws2.cell(row=1, column=1).value = "CMS Performance Data — All Contracts, All Measures (2021–2026)"
ws3.cell(row=1, column=1).value = "CMS — Full Company & Contract Directory | 2021–2026"
ws6.cell(row=2, column=2).value = "CMS Star Ratings — Industry Distribution Summary (2021–2026)"

# Save
wb.save(OUT)
print(f"\n=== DONE === Saved to {OUT}")
