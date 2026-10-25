"""Generate GenAI Pipeline Steps Excel matching the user's existing format."""
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "GenAI Pipeline"

# Column widths
ws.column_dimensions["A"].width = 6
ws.column_dimensions["B"].width = 32
ws.column_dimensions["C"].width = 30
ws.column_dimensions["D"].width = 35
ws.column_dimensions["E"].width = 28
ws.column_dimensions["F"].width = 38

# Styles
header_font = Font(name="Arial", bold=True, size=11)
header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
data_font = Font(name="Arial", size=11)
thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)
wrap = Alignment(wrap_text=True, vertical="top")

# Headers
headers = ["Step", "Activity", "Data Input", "Reference Data", "Output Data"]
for col, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.border = thin_border
    cell.alignment = Alignment(vertical="top")

# Data rows — existing 2 + 8 new GenAI rows
rows = [
    # Existing
    [1, "Gap Identification", "structural data", "reference guidelines", "score / compliance rate"],
    [2, "Propensity Score", "member demographics, claims\nhistory, pharmacy fills,\nprior outreach response", "CMS star rating cut points,\nHEDIS measure benchmarks", "member-level closure\npropensity score (0-1),\nrisk tier (high/med/low)"],
    # New GenAI rows
    [3, "Member Message Generation\n(GenAI)", "member gaps, demographics,\nlanguage preference", "HEDIS measure definitions,\nplan benefits summary", "personalized SMS / email /\nvoice script per member"],
    [4, "AI Voice Conversation\n(GenAI)", "real-time member speech\n(speech-to-text)", "conversation history,\nmember care gaps", "AI spoken response,\nappointment booking,\ncall transcript"],
    [5, "Next Best Action Scoring\n(GenAI)", "propensity score, channel\nhistory, gap urgency", "campaign performance data,\nSLA rules", "recommended channel +\ntiming + message type\nper member"],
    [6, "Cohort Dynamic Re-ranking\nof Member (GenAI)", "new claims, pharmacy fills,\ncall center logs, recent\nlab results, appointment\nno-shows, outreach responses", "CMS cut points,\nmeasure thresholds,\nprior propensity scores,\nhistorical closure rates\nby member segment", "updated member priority\nscores, re-ranked outreach\nqueue, member tier migration\n(high→critical), flagged\nmembers nearing measure\ndeadlines"],
    [7, "Interaction Sentiment\nAnalysis (GenAI)", "call transcripts, SMS replies,\nemail responses", "sentiment lexicon,\ncompliance keywords", "engagement score,\nescalation flag,\nfollow-up recommendation"],
    [8, "Auto-Summarization\n(GenAI)", "full call transcript, DTMF\nselections, AI conversation turns", "member profile, open gaps", "2-3 sentence interaction\nsummary for care coordinator"],
    [9, "Campaign Strategy\nOptimization (GenAI)", "campaign ROI, closure rates\nby channel / cohort", "historical benchmarks,\nbudget constraints", "recommended budget allocation,\nchannel mix, send cadence"],
    [10, "Intelligent Appointment\nMatching (GenAI)", "member availability signals,\nprovider schedules, geography", "facility capacity, travel time", "optimal appointment slot +\nprovider + location"],
    [11, "CAHPS NLP Sentiment\nAnalysis (GenAI)", "CAHPS free-text survey\nresponses, call center\ntranscripts, complaint logs", "CAHPS domain taxonomy\n(Getting Needed Care,\nPlan Communication, etc.),\nCMS weighting factors", "sentiment polarity per domain\n(positive/neutral/negative),\ntheme clusters, actionable\ninsight summaries,\npredicted CAHPS score impact"],
]

for r_idx, row_data in enumerate(rows, 2):
    for c_idx, val in enumerate(row_data, 1):
        cell = ws.cell(row=r_idx, column=c_idx, value=val if val != "" else None)
        cell.font = data_font
        cell.border = thin_border
        cell.alignment = wrap

# Set row heights for wrapped text
for r in range(2, len(rows) + 2):
    ws.row_dimensions[r].height = 45

out = r"C:\STARS_FInal_Draft\StarPulse_GenAI_Pipeline_Steps_v2.xlsx"
wb.save(out)
print(f"Saved: {out}")
