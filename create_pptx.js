const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "StarPulse Engineering";
pres.title = "StarPulse Omnichannel Outreach — Twilio Integration Architecture";

// ── Color Palette (EXL + Dark Executive) ──
const C = {
  navy: "1A1A2E",
  darkBg: "0F172A",
  cardBg: "1E293B",
  orange: "F26722",
  white: "FFFFFF",
  light: "F8FAFC",
  gray: "94A3B8",
  grayDark: "64748B",
  green: "10B981",
  purple: "8B5CF6",
  blue: "3B82F6",
  teal: "14B8A6",
  red: "EF4444",
  amber: "F59E0B",
};

const mkShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.2 });

// ════════════════════════════════════════════
// SLIDE 1 — Title
// ════════════════════════════════════════════
let s1 = pres.addSlide();
s1.background = { color: C.darkBg };

s1.addText("STARPULSE", {
  x: 0.8, y: 0.6, w: 8.4, h: 0.5,
  fontSize: 14, fontFace: "Calibri", color: C.orange, bold: true, charSpacing: 8,
});

s1.addText("Omnichannel Outreach\nIntegration Architecture", {
  x: 0.8, y: 1.2, w: 8.4, h: 2.0,
  fontSize: 40, fontFace: "Calibri", color: C.white, bold: true, lineSpacingMultiple: 1.1,
});

s1.addText("Voice Calls  |  SMS  |  Email  |  AI Care Coordinator", {
  x: 0.8, y: 3.2, w: 8.4, h: 0.5,
  fontSize: 16, fontFace: "Calibri", color: C.gray, italic: true,
});

s1.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 4.0, w: 1.2, h: 0.04, fill: { color: C.orange } });

s1.addText("EXL Services  |  Medicare Stars Platform  |  Confidential", {
  x: 0.8, y: 4.3, w: 8.4, h: 0.4,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

s1.addText("June 2026", {
  x: 0.8, y: 4.8, w: 8.4, h: 0.4,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});


// ════════════════════════════════════════════
// SLIDE 2 — Architecture Overview
// ════════════════════════════════════════════
let s2 = pres.addSlide();
s2.background = { color: C.light };

s2.addText("System Architecture Overview", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s2.addText("End-to-end outreach pipeline: FastAPI backend on Databricks Apps, Twilio serverless webhooks, and real-time audit logging", {
  x: 0.6, y: 0.85, w: 8.8, h: 0.4,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

// Architecture boxes
const archBoxes = [
  { label: "StarPulse UI", sub: "stars_v2.html\nSingle-page app", x: 0.6, color: C.blue },
  { label: "FastAPI Backend", sub: "Databricks Apps\nUvicorn / Python", x: 2.65, color: C.orange },
  { label: "Twilio API", sub: "Voice / SMS\nREST API", x: 4.7, color: C.red },
  { label: "Twilio Functions", sub: "Serverless JS\nPublic webhooks", x: 6.75, color: C.purple },
];

archBoxes.forEach(b => {
  s2.addShape(pres.shapes.RECTANGLE, {
    x: b.x, y: 1.55, w: 1.8, h: 1.3,
    fill: { color: C.white },
    line: { color: b.color, width: 2 },
    shadow: mkShadow(),
  });
  s2.addText(b.label, {
    x: b.x, y: 1.6, w: 1.8, h: 0.45,
    fontSize: 12, fontFace: "Calibri", color: b.color, bold: true, align: "center", valign: "middle", margin: 0,
  });
  s2.addText(b.sub, {
    x: b.x, y: 2.05, w: 1.8, h: 0.7,
    fontSize: 9, fontFace: "Calibri", color: C.grayDark, align: "center", valign: "top", margin: 0,
  });
});

// Arrows between boxes
[1.05, 3.1, 5.15].forEach(ax => {
  s2.addShape(pres.shapes.LINE, {
    x: ax + 1.4, y: 2.2, w: 0.65, h: 0,
    line: { color: C.gray, width: 1.5, dashType: "dash" },
  });
});

// Bottom row — data stores
const dataBoxes = [
  { label: "Databricks SQL", sub: "outreach_activity_log\nverified_contacts", x: 2.65, color: C.teal },
  { label: "Claude API", sub: "Anthropic\nclaude-haiku-4-5", x: 4.7, color: C.purple },
  { label: "SendGrid", sub: "Email delivery\nSMTP API", x: 6.75, color: C.green },
];

dataBoxes.forEach(b => {
  s2.addShape(pres.shapes.RECTANGLE, {
    x: b.x, y: 3.4, w: 1.8, h: 1.1,
    fill: { color: C.white },
    line: { color: b.color, width: 1.5, dashType: "dash" },
    shadow: mkShadow(),
  });
  s2.addText(b.label, {
    x: b.x, y: 3.45, w: 1.8, h: 0.4,
    fontSize: 11, fontFace: "Calibri", color: b.color, bold: true, align: "center", valign: "middle", margin: 0,
  });
  s2.addText(b.sub, {
    x: b.x, y: 3.85, w: 1.8, h: 0.55,
    fontSize: 9, fontFace: "Calibri", color: C.grayDark, align: "center", valign: "top", margin: 0,
  });
});

// Vertical connectors
[2.65, 4.7, 6.75].forEach(cx => {
  s2.addShape(pres.shapes.LINE, {
    x: cx + 0.9, y: 2.85, w: 0, h: 0.55,
    line: { color: C.gray, width: 1, dashType: "dot" },
  });
});

// Footer note
s2.addText("Databricks Apps enforce OAuth/SSO on all inbound requests. Twilio Functions (serverless) serve as public webhook handlers, bypassing the 401 auth barrier for external callbacks.", {
  x: 0.6, y: 4.8, w: 8.8, h: 0.5,
  fontSize: 9, fontFace: "Calibri", color: C.grayDark, italic: true,
});


// ════════════════════════════════════════════
// SLIDE 3 — Voice Call: Complete Flow
// ════════════════════════════════════════════
let s3 = pres.addSlide();
s3.background = { color: C.light };

s3.addText("Voice Call — Interactive DTMF Flow", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s3.addText("Twilio places the call with inline TwiML. Member keypresses route through Twilio Functions for real-time interaction.", {
  x: 0.6, y: 0.85, w: 8.8, h: 0.35,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

// Flow steps
const flowSteps = [
  { num: "1", title: "Call Initiated", desc: "FastAPI calls Twilio REST API\nwith inline TwiML + script", color: C.blue },
  { num: "2", title: "Script Played", desc: "Polly.Joanna reads AI-generated\nscript about the care gap", color: C.orange },
  { num: "3", title: "DTMF Menu", desc: "<Gather numDigits=\"1\">\nPress 1: Schedule\nPress 2: AI Agent", color: C.teal },
  { num: "4", title: "Webhook", desc: "Twilio POSTs digit to\ntwil.io/call-gather\n(Twilio Function)", color: C.purple },
];

flowSteps.forEach((step, i) => {
  const x = 0.6 + i * 2.3;
  // Number circle
  s3.addShape(pres.shapes.OVAL, {
    x: x + 0.55, y: 1.4, w: 0.5, h: 0.5,
    fill: { color: step.color },
  });
  s3.addText(step.num, {
    x: x + 0.55, y: 1.4, w: 0.5, h: 0.5,
    fontSize: 16, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle",
  });
  // Title
  s3.addText(step.title, {
    x: x, y: 2.0, w: 1.6, h: 0.35,
    fontSize: 12, fontFace: "Calibri", color: C.darkBg, bold: true, align: "center", margin: 0,
  });
  // Desc
  s3.addText(step.desc, {
    x: x, y: 2.35, w: 1.6, h: 0.75,
    fontSize: 9, fontFace: "Calibri", color: C.grayDark, align: "center", margin: 0,
  });
  // Arrow
  if (i < 3) {
    s3.addShape(pres.shapes.LINE, {
      x: x + 1.6, y: 1.65, w: 0.7, h: 0,
      line: { color: C.gray, width: 1.5 },
    });
  }
});

// Branching section
s3.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 3.3, w: 4.2, h: 0.04, fill: { color: C.orange } });

// Press 1 box
s3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 3.5, w: 4.2, h: 1.6,
  fill: { color: C.white }, line: { color: C.green, width: 1.5 }, shadow: mkShadow(),
});
s3.addText("Press 1 — Appointment Scheduling", {
  x: 0.8, y: 3.55, w: 3.8, h: 0.35,
  fontSize: 13, fontFace: "Calibri", color: C.green, bold: true, margin: 0,
});
s3.addText([
  { text: "1. Twilio Function returns time slot sub-menu", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "2. <Gather> captures slot digit (1-4)", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "3. /call-slot confirms booking via TwiML <Say>", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "4. Logs to Databricks: member_selection = \"Scheduled: tomorrow 9 AM\"", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "5. Interaction appended to timestamped audit trail", options: { bullet: true, fontSize: 10 } },
], {
  x: 0.8, y: 3.9, w: 3.8, h: 1.1,
  fontFace: "Calibri", color: C.grayDark, paraSpaceAfter: 2,
});

// Press 2 box
s3.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 3.5, w: 4.2, h: 1.6,
  fill: { color: C.white }, line: { color: C.purple, width: 1.5 }, shadow: mkShadow(),
});
s3.addText("Press 2 — AI Care Coordinator", {
  x: 5.4, y: 3.55, w: 3.8, h: 0.35,
  fontSize: 13, fontFace: "Calibri", color: C.purple, bold: true, margin: 0,
});
s3.addText([
  { text: "1. <Gather input=\"speech\"> captures member voice", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "2. Speech-to-text sent to /call-agent Function", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "3. Function calls Claude API (haiku-4-5, 200 tokens)", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "4. AI response spoken back via <Say>, loop continues", options: { bullet: true, breakLine: true, fontSize: 10 } },
  { text: "5. Goodbye detection ends call, logs \"AI completed\"", options: { bullet: true, fontSize: 10 } },
], {
  x: 5.4, y: 3.9, w: 3.8, h: 1.1,
  fontFace: "Calibri", color: C.grayDark, paraSpaceAfter: 2,
});


// ════════════════════════════════════════════
// SLIDE 4 — Press 1: Appointment Scheduling Deep Dive
// ════════════════════════════════════════════
let s4 = pres.addSlide();
s4.background = { color: C.light };

s4.addText("Press 1 — Appointment Scheduling (DTMF)", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

// Sequence diagram as steps
const seqSteps = [
  { from: "Member", to: "Twilio", msg: "Presses 1", y: 1.2 },
  { from: "Twilio", to: "call-gather", msg: "POST Digits=1, CallSid", y: 1.7 },
  { from: "call-gather", to: "Databricks", msg: "SQL UPDATE status='scheduling'", y: 2.2 },
  { from: "call-gather", to: "Twilio", msg: "TwiML: <Gather> slot menu (1-4)", y: 2.7 },
  { from: "Member", to: "Twilio", msg: "Presses slot digit", y: 3.2 },
  { from: "Twilio", to: "call-slot", msg: "POST Digits=N, CallSid", y: 3.7 },
  { from: "call-slot", to: "Databricks", msg: "SQL UPDATE member_selection='Scheduled: ...'", y: 4.2 },
  { from: "call-slot", to: "Twilio", msg: "TwiML: <Say> Confirmation + Goodbye", y: 4.7 },
];

// Column headers
const cols = { "Member": 1.2, "Twilio": 3.2, "call-gather": 5.2, "call-slot": 7.0, "Databricks": 8.8 };
Object.entries(cols).forEach(([label, x]) => {
  s4.addShape(pres.shapes.RECTANGLE, {
    x: x - 0.5, y: 0.85, w: 1.0, h: 0.3,
    fill: { color: label === "Member" ? C.blue : label === "Twilio" ? C.red : label === "Databricks" ? C.teal : C.purple },
  });
  s4.addText(label, {
    x: x - 0.5, y: 0.85, w: 1.0, h: 0.3,
    fontSize: 8, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle",
  });
});

// Sequence arrows
seqSteps.forEach(step => {
  const fromX = cols[step.from];
  const toX = cols[step.to];
  const minX = Math.min(fromX, toX);
  const w = Math.abs(toX - fromX);
  s4.addShape(pres.shapes.LINE, {
    x: minX, y: step.y, w: w, h: 0,
    line: { color: C.grayDark, width: 1 },
  });
  s4.addText(step.msg, {
    x: minX - 0.2, y: step.y - 0.22, w: w + 0.4, h: 0.2,
    fontSize: 8, fontFace: "Calibri", color: C.darkBg, align: "center", margin: 0,
  });
});

// Time slot table
s4.addText("Available Slots: 1→Tomorrow 9AM  |  2→Tomorrow 2PM  |  3→Friday 10AM  |  4→Callback Request", {
  x: 0.6, y: 5.1, w: 8.8, h: 0.3,
  fontSize: 9, fontFace: "Consolas", color: C.grayDark, italic: true,
});


// ════════════════════════════════════════════
// SLIDE 5 — Press 2: AI Care Coordinator Deep Dive
// ════════════════════════════════════════════
let s5 = pres.addSlide();
s5.background = { color: C.light };

s5.addText("Press 2 — AI Care Coordinator (Claude)", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s5.addText("Real-time voice conversation loop: Twilio speech-to-text → Claude AI → text-to-speech, running entirely on Twilio Functions.", {
  x: 0.6, y: 0.85, w: 8.8, h: 0.35,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

// Conversation loop diagram
const loopSteps = [
  { num: "1", title: "Speech Capture", desc: "<Gather input=\"speech\">\nspeechTimeout: 2s\nlanguage: en-US", x: 0.6, color: C.blue },
  { num: "2", title: "STT Result", desc: "Twilio POSTs\nSpeechResult to\n/call-agent", x: 2.95, color: C.orange },
  { num: "3", title: "Claude API", desc: "Anthropic Messages API\nmodel: claude-haiku-4-5\nmax_tokens: 200", x: 5.3, color: C.purple },
  { num: "4", title: "TTS Response", desc: "<Say voice=\"Polly.Joanna\">\nAI reply spoken back\nLoop or end call", x: 7.65, color: C.green },
];

loopSteps.forEach((step, i) => {
  s5.addShape(pres.shapes.RECTANGLE, {
    x: step.x, y: 1.4, w: 2.1, h: 1.5,
    fill: { color: C.white }, line: { color: step.color, width: 1.5 }, shadow: mkShadow(),
  });
  s5.addShape(pres.shapes.OVAL, {
    x: step.x + 0.8, y: 1.5, w: 0.4, h: 0.4,
    fill: { color: step.color },
  });
  s5.addText(step.num, {
    x: step.x + 0.8, y: 1.5, w: 0.4, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle",
  });
  s5.addText(step.title, {
    x: step.x + 0.1, y: 1.95, w: 1.9, h: 0.3,
    fontSize: 12, fontFace: "Calibri", color: step.color, bold: true, align: "center", margin: 0,
  });
  s5.addText(step.desc, {
    x: step.x + 0.1, y: 2.25, w: 1.9, h: 0.6,
    fontSize: 9, fontFace: "Consolas", color: C.grayDark, align: "center", margin: 0,
  });
  if (i < 3) {
    s5.addShape(pres.shapes.LINE, {
      x: step.x + 2.1, y: 2.15, w: 0.85, h: 0,
      line: { color: C.gray, width: 1.5 },
    });
  }
});

// Loop back arrow text
s5.addShape(pres.shapes.RECTANGLE, {
  x: 2.5, y: 3.1, w: 5.0, h: 0.35,
  fill: { color: C.purple, transparency: 10 },
});
s5.addText("Loop continues until goodbye detected (\"bye\", \"take care\", \"have a great day\")", {
  x: 2.5, y: 3.1, w: 5.0, h: 0.35,
  fontSize: 10, fontFace: "Calibri", color: C.purple, bold: true, align: "center", valign: "middle",
});

// Technical details
s5.addText("Technical Details", {
  x: 0.6, y: 3.7, w: 8.8, h: 0.35,
  fontSize: 16, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

const techDetails = [
  ["System Prompt", "Medicare care coordinator persona. Short responses (1-3 sentences). Empathetic, professional. Offers scheduling. Never provides medical diagnoses."],
  ["Conversation State", "In-memory dictionary keyed by CallSid. Auto-evicts after 30 entries. Cleared on goodbye."],
  ["Latency", "Claude haiku-4-5 responds in ~500ms. Total round-trip (STT + AI + TTS): ~2-3 seconds."],
  ["Audit Trail", "Each speech turn logged to Databricks via SQL Statement API. Final status: ai-completed / ai-failed."],
];

techDetails.forEach((row, i) => {
  const y = 4.1 + i * 0.38;
  s5.addText(row[0], {
    x: 0.6, y, w: 1.8, h: 0.35,
    fontSize: 10, fontFace: "Calibri", color: C.orange, bold: true, valign: "top", margin: 0,
  });
  s5.addText(row[1], {
    x: 2.5, y, w: 7.0, h: 0.35,
    fontSize: 10, fontFace: "Calibri", color: C.grayDark, valign: "top", margin: 0,
  });
});


// ════════════════════════════════════════════
// SLIDE 6 — SMS Integration
// ════════════════════════════════════════════
let s6 = pres.addSlide();
s6.background = { color: C.light };

s6.addText("SMS Integration — Twilio Messaging API", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s6.addText("Bulk and individual SMS outreach with AI-generated personalized messaging and delivery tracking.", {
  x: 0.6, y: 0.85, w: 8.8, h: 0.35,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

// Flow
const smsFlow = [
  { num: "1", title: "Message Generation", desc: "Claude generates personalized\nSMS content per member based\non care gap and measure data", color: C.purple },
  { num: "2", title: "Twilio REST API", desc: "client.messages.create()\nbody, from_, to\nReturns MessageSid", color: C.red },
  { num: "3", title: "Delivery Tracking", desc: "SID stored in outreach_activity_log\nStatus synced via Twilio API\n(sent → delivered / failed)", color: C.teal },
];

smsFlow.forEach((step, i) => {
  const x = 0.6 + i * 3.2;
  s6.addShape(pres.shapes.RECTANGLE, {
    x, y: 1.5, w: 2.8, h: 1.8,
    fill: { color: C.white }, line: { color: step.color, width: 1.5 }, shadow: mkShadow(),
  });
  s6.addShape(pres.shapes.OVAL, {
    x: x + 1.15, y: 1.6, w: 0.5, h: 0.5,
    fill: { color: step.color },
  });
  s6.addText(step.num, {
    x: x + 1.15, y: 1.6, w: 0.5, h: 0.5,
    fontSize: 16, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle",
  });
  s6.addText(step.title, {
    x: x + 0.1, y: 2.15, w: 2.6, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: step.color, bold: true, align: "center", margin: 0,
  });
  s6.addText(step.desc, {
    x: x + 0.1, y: 2.5, w: 2.6, h: 0.7,
    fontSize: 10, fontFace: "Calibri", color: C.grayDark, align: "center", margin: 0,
  });
});

// Code snippet
s6.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 3.6, w: 8.8, h: 1.6,
  fill: { color: C.cardBg },
});

s6.addText("Implementation", {
  x: 0.8, y: 3.65, w: 3, h: 0.3,
  fontSize: 10, fontFace: "Calibri", color: C.orange, bold: true, margin: 0,
});

s6.addText([
  { text: "def send_sms(to_number: str, body: str) -> tuple[bool, str]:", options: { breakLine: true } },
  { text: "    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)", options: { breakLine: true } },
  { text: "    message = client.messages.create(", options: { breakLine: true } },
  { text: "        body=body, from_=settings.twilio_from_number, to=to_number)", options: { breakLine: true } },
  { text: "    return True, message.sid  # SID logged to outreach_activity_log", options: {} },
], {
  x: 0.8, y: 3.95, w: 8.4, h: 1.2,
  fontSize: 9, fontFace: "Consolas", color: C.green, margin: 0,
});


// ════════════════════════════════════════════
// SLIDE 7 — Email Integration
// ════════════════════════════════════════════
let s7 = pres.addSlide();
s7.background = { color: C.light };

s7.addText("Email Integration — SendGrid API", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s7.addText("Personalized email outreach via SendGrid with AI-crafted content and delivery status tracking.", {
  x: 0.6, y: 0.85, w: 8.8, h: 0.35,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

// Flow
const emailFlow = [
  { num: "1", title: "Content Generation", desc: "Claude crafts email subject\nand body personalized to\nmember's care gap", color: C.purple },
  { num: "2", title: "SendGrid API", desc: "SendGridAPIClient.send()\nMail(from, to, subject, body)\nReturns HTTP status code", color: C.green },
  { num: "3", title: "Status Logging", desc: "HTTP 202 = accepted\nLogged to outreach_activity_log\nwith channel='Email'", color: C.teal },
];

emailFlow.forEach((step, i) => {
  const x = 0.6 + i * 3.2;
  s7.addShape(pres.shapes.RECTANGLE, {
    x, y: 1.5, w: 2.8, h: 1.8,
    fill: { color: C.white }, line: { color: step.color, width: 1.5 }, shadow: mkShadow(),
  });
  s7.addShape(pres.shapes.OVAL, {
    x: x + 1.15, y: 1.6, w: 0.5, h: 0.5,
    fill: { color: step.color },
  });
  s7.addText(step.num, {
    x: x + 1.15, y: 1.6, w: 0.5, h: 0.5,
    fontSize: 16, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle",
  });
  s7.addText(step.title, {
    x: x + 0.1, y: 2.15, w: 2.6, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: step.color, bold: true, align: "center", margin: 0,
  });
  s7.addText(step.desc, {
    x: x + 0.1, y: 2.5, w: 2.6, h: 0.7,
    fontSize: 10, fontFace: "Calibri", color: C.grayDark, align: "center", margin: 0,
  });
});

// Comparison table
s7.addText("Channel Comparison", {
  x: 0.6, y: 3.6, w: 8.8, h: 0.4,
  fontSize: 16, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

const tableRows = [
  [
    { text: "Channel", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "center" } },
    { text: "Provider", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "center" } },
    { text: "Latency", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "center" } },
    { text: "AI-Powered", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "center" } },
    { text: "Audit Logged", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "center" } },
  ],
  [
    { text: "Voice (Press 1)", options: { align: "center" } },
    { text: "Twilio Voice", options: { align: "center" } },
    { text: "Real-time", options: { align: "center" } },
    { text: "Script generation", options: { align: "center" } },
    { text: "Yes — full trail", options: { align: "center", color: C.green } },
  ],
  [
    { text: "Voice (Press 2)", options: { align: "center" } },
    { text: "Twilio + Claude", options: { align: "center" } },
    { text: "~2-3s per turn", options: { align: "center" } },
    { text: "Live conversation", options: { align: "center" } },
    { text: "Yes — each turn", options: { align: "center", color: C.green } },
  ],
  [
    { text: "SMS", options: { align: "center" } },
    { text: "Twilio Messaging", options: { align: "center" } },
    { text: "< 5 seconds", options: { align: "center" } },
    { text: "Content generation", options: { align: "center" } },
    { text: "Yes — SID tracked", options: { align: "center", color: C.green } },
  ],
  [
    { text: "Email", options: { align: "center" } },
    { text: "SendGrid", options: { align: "center" } },
    { text: "< 3 seconds", options: { align: "center" } },
    { text: "Content generation", options: { align: "center" } },
    { text: "Yes — status code", options: { align: "center", color: C.green } },
  ],
];

s7.addTable(tableRows, {
  x: 0.6, y: 4.05, w: 8.8,
  fontSize: 10, fontFace: "Calibri",
  border: { pt: 0.5, color: "E2E8F0" },
  colW: [1.6, 1.6, 1.4, 2.0, 2.2],
  rowH: [0.3, 0.28, 0.28, 0.28, 0.28],
});


// ════════════════════════════════════════════
// SLIDE 8 — Twilio Functions Architecture
// ════════════════════════════════════════════
let s8 = pres.addSlide();
s8.background = { color: C.light };

s8.addText("Twilio Functions — Serverless Webhook Layer", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s8.addText("Why: Databricks Apps enforce OAuth/SSO on all inbound HTTP — Twilio's POST callbacks receive HTTP 401. Twilio Functions provide public, serverless endpoints.", {
  x: 0.6, y: 0.85, w: 8.8, h: 0.4,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

// 3 Functions
const funcs = [
  {
    name: "/call-gather",
    desc: "Main DTMF router",
    details: [
      "Receives: Digits, CallSid",
      "Digit 1 → returns slot menu TwiML",
      "Digit 2 → returns speech gather TwiML",
      "Logs selection to Databricks SQL API",
    ],
    color: C.orange,
  },
  {
    name: "/call-slot",
    desc: "Time slot confirmation",
    details: [
      "Receives: Digits (1-4), CallSid",
      "Maps digit to appointment slot",
      "Returns confirmation <Say>",
      "Logs: member_selection = slot text",
    ],
    color: C.green,
  },
  {
    name: "/call-agent",
    desc: "AI conversation loop",
    details: [
      "Receives: SpeechResult, CallSid",
      "Calls Claude API via HTTPS",
      "Returns <Gather> + <Say> loop",
      "Goodbye detection ends the call",
    ],
    color: C.purple,
  },
];

funcs.forEach((fn, i) => {
  const x = 0.6 + i * 3.2;
  s8.addShape(pres.shapes.RECTANGLE, {
    x, y: 1.5, w: 2.8, h: 2.6,
    fill: { color: C.white }, line: { color: fn.color, width: 1.5 }, shadow: mkShadow(),
  });
  s8.addText(fn.name, {
    x: x + 0.1, y: 1.55, w: 2.6, h: 0.35,
    fontSize: 14, fontFace: "Consolas", color: fn.color, bold: true, align: "center", margin: 0,
  });
  s8.addText(fn.desc, {
    x: x + 0.1, y: 1.9, w: 2.6, h: 0.25,
    fontSize: 10, fontFace: "Calibri", color: C.grayDark, align: "center", margin: 0,
  });
  s8.addShape(pres.shapes.LINE, {
    x: x + 0.3, y: 2.2, w: 2.2, h: 0,
    line: { color: "E2E8F0", width: 0.5 },
  });
  fn.details.forEach((d, j) => {
    s8.addText(d, {
      x: x + 0.2, y: 2.3 + j * 0.35, w: 2.4, h: 0.3,
      fontSize: 9, fontFace: "Calibri", color: C.grayDark, bullet: true, margin: 0,
    });
  });
});

// Infrastructure details
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.4, w: 8.8, h: 0.9,
  fill: { color: C.cardBg },
});

s8.addText("Infrastructure", {
  x: 0.8, y: 4.45, w: 3, h: 0.25,
  fontSize: 10, fontFace: "Calibri", color: C.orange, bold: true, margin: 0,
});

s8.addText([
  { text: "Runtime: Node.js 22  |  Domain: starpulse-webhooks-1622-prod.twil.io  |  Visibility: Public", options: { breakLine: true } },
  { text: "Env Vars: ANTHROPIC_API_KEY, DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE", options: {} },
], {
  x: 0.8, y: 4.7, w: 8.4, h: 0.55,
  fontSize: 9, fontFace: "Consolas", color: C.green, margin: 0,
});


// ════════════════════════════════════════════
// SLIDE 9 — Audit Trail & Databricks Logging
// ════════════════════════════════════════════
let s9 = pres.addSlide();
s9.background = { color: C.light };

s9.addText("Audit Trail & Databricks Logging", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s9.addText("Every outreach interaction is persisted to aiagenticdemo.stars_silver.outreach_activity_log with a timestamped audit trail.", {
  x: 0.6, y: 0.85, w: 8.8, h: 0.35,
  fontSize: 11, fontFace: "Calibri", color: C.grayDark,
});

// Table schema
const schemaRows = [
  [
    { text: "Column", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "left" } },
    { text: "Type", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "center" } },
    { text: "Description", options: { bold: true, color: "FFFFFF", fill: { color: C.darkBg }, align: "left" } },
  ],
  ["id", "BIGINT", "Auto-increment primary key"],
  ["created_at", "TIMESTAMP", "When outreach was initiated"],
  ["member_name", "STRING", "Target member display name"],
  ["channel", "STRING", "Call / SMS / Email"],
  ["contact_used", "STRING", "Phone number or email used"],
  ["status", "STRING", "initiated → scheduling → scheduled / ai-completed / delivered / failed"],
  ["provider_sid", "STRING", "Twilio Call SID or Message SID"],
  ["member_selection", "STRING", "Final choice: \"Scheduled: tomorrow 9 AM\" / \"AI conversation completed\" / \"No time slot selected\""],
  ["interaction_log", "STRING", "Timestamped trail: [HH:MM:SS] status: detail | [HH:MM:SS] ..."],
  ["script_body", "STRING", "AI-generated script that was read to the member"],
];

s9.addTable(schemaRows, {
  x: 0.6, y: 1.4, w: 8.8,
  fontSize: 9, fontFace: "Calibri",
  border: { pt: 0.5, color: "E2E8F0" },
  colW: [1.6, 1.0, 6.2],
  rowH: [0.28, 0.25, 0.25, 0.25, 0.25, 0.25, 0.28, 0.25, 0.33, 0.33, 0.25],
});

// Example log
s9.addText("Example interaction_log value:", {
  x: 0.6, y: 4.5, w: 8.8, h: 0.3,
  fontSize: 10, fontFace: "Calibri", color: C.darkBg, bold: true, margin: 0,
});

s9.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.8, w: 8.8, h: 0.55,
  fill: { color: C.cardBg },
});
s9.addText("[12:04:31] scheduling: Member pressed 1  |  [12:04:38] scheduled: Slot selected: tomorrow morning at 9 AM", {
  x: 0.8, y: 4.85, w: 8.4, h: 0.45,
  fontSize: 9, fontFace: "Consolas", color: C.green, margin: 0,
});


// ════════════════════════════════════════════
// SLIDE 10 — Security & Key Decisions
// ════════════════════════════════════════════
let s10 = pres.addSlide();
s10.background = { color: C.darkBg };

s10.addText("Security & Architectural Decisions", {
  x: 0.6, y: 0.3, w: 8.8, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.white, bold: true, margin: 0,
});

const decisions = [
  {
    title: "Databricks OAuth Bypass",
    desc: "Databricks Apps enforce OAuth/SSO on all HTTP. External services (Twilio) get 401. Solution: Twilio Functions as a public serverless layer that calls Databricks SQL API with a PAT token for logging.",
    color: C.orange,
  },
  {
    title: "No Hardcoded Phone Numbers",
    desc: "All contact numbers are read from the verified_contacts table at call time. If no active contact exists, the call fails with a clear error instead of dialing a wrong number.",
    color: C.green,
  },
  {
    title: "Background Task Pattern",
    desc: "Twilio has a 15-second webhook timeout. DB writes run as FastAPI BackgroundTasks (local) or fire-and-forget HTTPS (Functions) to avoid blocking the TwiML response.",
    color: C.blue,
  },
  {
    title: "AI Safety Guardrails",
    desc: "Claude system prompt prohibits medical diagnoses. Responses capped at 200 tokens for voice brevity. API key validated before call — graceful fallback if missing.",
    color: C.purple,
  },
];

decisions.forEach((d, i) => {
  const y = 1.1 + i * 1.05;
  s10.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y, w: 8.8, h: 0.9,
    fill: { color: C.cardBg },
  });
  s10.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y, w: 0.06, h: 0.9,
    fill: { color: d.color },
  });
  s10.addText(d.title, {
    x: 0.9, y: y + 0.05, w: 8.3, h: 0.3,
    fontSize: 13, fontFace: "Calibri", color: d.color, bold: true, margin: 0,
  });
  s10.addText(d.desc, {
    x: 0.9, y: y + 0.35, w: 8.3, h: 0.5,
    fontSize: 10, fontFace: "Calibri", color: C.gray, margin: 0,
  });
});


// ════════════════════════════════════════════
// SLIDE 11 — Thank You
// ════════════════════════════════════════════
let s11 = pres.addSlide();
s11.background = { color: C.darkBg };

s11.addText("STARPULSE", {
  x: 0.8, y: 1.5, w: 8.4, h: 0.5,
  fontSize: 14, fontFace: "Calibri", color: C.orange, bold: true, charSpacing: 8,
});

s11.addText("Thank You", {
  x: 0.8, y: 2.0, w: 8.4, h: 1.0,
  fontSize: 44, fontFace: "Calibri", color: C.white, bold: true,
});

s11.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 3.2, w: 1.2, h: 0.04, fill: { color: C.orange } });

s11.addText("EXL Services  |  Medicare Stars Platform", {
  x: 0.8, y: 3.5, w: 8.4, h: 0.4,
  fontSize: 14, fontFace: "Calibri", color: C.gray,
});

s11.addText("Questions?", {
  x: 0.8, y: 4.2, w: 8.4, h: 0.4,
  fontSize: 16, fontFace: "Calibri", color: C.grayDark, italic: true,
});


// ── Save ──
const outPath = process.argv[2] || "C:\\STARS_FInal_Draft\\StarPulse_Twilio_Integration.pptx";
pres.writeFile({ fileName: outPath }).then(() => {
  console.log("Presentation saved to: " + outPath);
}).catch(err => {
  console.error("Error:", err);
});
