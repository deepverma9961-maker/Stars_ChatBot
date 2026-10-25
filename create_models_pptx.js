const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "StarPulse Engineering";
pres.title = "StarPulse — AI Models & Agents Architecture";

// ── Palette: Ocean Gradient (deep tech feel) ──
const C = {
  navy:    "1E2761",
  darkBg:  "0F1629",
  ice:     "CADCFC",
  white:   "FFFFFF",
  orange:  "F26722",
  accent:  "3B82F6",
  teal:    "0EA5E9",
  green:   "10B981",
  purple:  "8B5CF6",
  gray:    "94A3B8",
  darkGray:"334155",
  lightBg: "F8FAFC",
  cardBg:  "1E293B",
  bodyText:"E2E8F0",
};

const mkShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.2, angle: 135 });

// ════════════════════════════════════════════════════════════════
// SLIDE 1 — Title
// ════════════════════════════════════════════════════════════════
let s1 = pres.addSlide();
s1.background = { color: C.darkBg };

s1.addText("EXL  |  StarPulse", {
  x: 0.8, y: 0.6, w: 8, h: 0.5,
  fontSize: 14, fontFace: "Calibri", color: C.orange,
  charSpacing: 4, bold: true,
});
s1.addText("AI Models & Agents\nArchitecture", {
  x: 0.8, y: 1.5, w: 7, h: 2.2,
  fontSize: 42, fontFace: "Calibri", color: C.white,
  bold: true, lineSpacingMultiple: 1.1,
});
s1.addText("Medicare Stars Platform — Intelligent Outreach & Predictive Analytics", {
  x: 0.8, y: 3.6, w: 8, h: 0.5,
  fontSize: 16, fontFace: "Calibri", color: C.ice,
});
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 4.3, w: 1.5, h: 0.06, fill: { color: C.orange },
});
s1.addText("June 2026  |  Confidential", {
  x: 0.8, y: 4.6, w: 4, h: 0.4,
  fontSize: 11, fontFace: "Calibri", color: C.gray,
});

// Right side — abstract AI pattern (stacked circles)
const circles = [
  { x: 7.8, y: 1.0, w: 1.8, h: 1.8, c: C.accent },
  { x: 8.6, y: 2.5, w: 1.2, h: 1.2, c: C.teal },
  { x: 7.2, y: 3.0, w: 0.9, h: 0.9, c: C.purple },
  { x: 8.2, y: 3.8, w: 0.6, h: 0.6, c: C.orange },
];
circles.forEach(c => {
  s1.addShape(pres.shapes.OVAL, {
    x: c.x, y: c.y, w: c.w, h: c.h,
    fill: { color: c.c, transparency: 70 },
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 2 — AI Landscape Overview
// ════════════════════════════════════════════════════════════════
let s2 = pres.addSlide();
s2.background = { color: C.lightBg };

s2.addText("AI & ML Landscape", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 30, fontFace: "Calibri", color: C.navy, bold: true,
});
s2.addText("Five distinct AI/ML components power StarPulse across voice, messaging, and analytics", {
  x: 0.6, y: 0.95, w: 9, h: 0.4,
  fontSize: 13, fontFace: "Calibri", color: C.darkGray,
});

// 5 cards in a row
const aiCards = [
  { title: "Voice Agent", sub: "Claude Haiku 4.5", desc: "Real-time phone\nconversations", color: C.accent },
  { title: "Message AI", sub: "Claude Haiku 4.5", desc: "SMS / Email / Call\nscript generation", color: C.teal },
  { title: "Twilio Agent", sub: "Claude Haiku 4.5", desc: "Serverless voice\nAI (Functions)", color: C.purple },
  { title: "Propensity ML", sub: "GradientBoosting", desc: "Gap closure\nprobability", color: C.green },
  { title: "Urgency ML", sub: "RandomForest", desc: "HOS fall-risk\nscoring (15-98)", color: C.orange },
];
aiCards.forEach((card, i) => {
  const cx = 0.5 + i * 1.85;
  s2.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: 1.6, w: 1.7, h: 3.4,
    fill: { color: C.white },
    shadow: mkShadow(),
  });
  // Top accent bar
  s2.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: 1.6, w: 1.7, h: 0.08, fill: { color: card.color },
  });
  // Circle icon placeholder
  s2.addShape(pres.shapes.OVAL, {
    x: cx + 0.5, y: 1.9, w: 0.7, h: 0.7,
    fill: { color: card.color, transparency: 85 },
  });
  s2.addText(i < 3 ? "LLM" : "ML", {
    x: cx + 0.5, y: 1.9, w: 0.7, h: 0.7,
    fontSize: 10, fontFace: "Calibri", color: card.color,
    bold: true, align: "center", valign: "middle",
  });
  s2.addText(card.title, {
    x: cx + 0.1, y: 2.75, w: 1.5, h: 0.45,
    fontSize: 12, fontFace: "Calibri", color: C.navy, bold: true, align: "center",
  });
  s2.addText(card.sub, {
    x: cx + 0.1, y: 3.15, w: 1.5, h: 0.35,
    fontSize: 9, fontFace: "Calibri", color: card.color, align: "center", bold: true,
  });
  s2.addText(card.desc, {
    x: cx + 0.1, y: 3.55, w: 1.5, h: 0.8,
    fontSize: 10, fontFace: "Calibri", color: C.darkGray, align: "center",
    lineSpacingMultiple: 1.2,
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 3 — Claude Haiku 4.5: Model Profile
// ════════════════════════════════════════════════════════════════
let s3 = pres.addSlide();
s3.background = { color: C.darkBg };

s3.addText("Claude Haiku 4.5 — Model Profile", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.white, bold: true,
});
s3.addText("All three LLM agents use Anthropic's Claude Haiku 4.5 — optimized for low-latency, cost-effective inference", {
  x: 0.6, y: 0.9, w: 9, h: 0.4,
  fontSize: 12, fontFace: "Calibri", color: C.ice,
});

// Left: specs table
const specRows = [
  ["Model ID", "claude-haiku-4-5"],
  ["Provider", "Anthropic (api.anthropic.com)"],
  ["API Version", "2023-06-01"],
  ["Max Tokens", "200 (voice) / 400 (messages)"],
  ["SDK", "anthropic Python (async) + raw HTTPS (JS)"],
  ["Latency", "< 1s typical (optimized for voice)"],
  ["Fallback", "Hardcoded templates if API unreachable"],
];
specRows.forEach((row, i) => {
  const ry = 1.55 + i * 0.5;
  s3.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: ry, w: 4.5, h: 0.45,
    fill: { color: i % 2 === 0 ? "1A2744" : "15203A" },
  });
  s3.addText(row[0], {
    x: 0.75, y: ry, w: 1.6, h: 0.45,
    fontSize: 11, fontFace: "Calibri", color: C.orange, bold: true, valign: "middle",
  });
  s3.addText(row[1], {
    x: 2.35, y: ry, w: 2.7, h: 0.45,
    fontSize: 11, fontFace: "Calibri", color: C.bodyText, valign: "middle",
  });
});

// Right: Why Haiku?
s3.addShape(pres.shapes.RECTANGLE, {
  x: 5.5, y: 1.55, w: 4.2, h: 3.5,
  fill: { color: C.cardBg },
  shadow: mkShadow(),
});
s3.addText("Why Claude Haiku 4.5?", {
  x: 5.8, y: 1.7, w: 3.6, h: 0.45,
  fontSize: 14, fontFace: "Calibri", color: C.teal, bold: true,
});
const reasons = [
  { t: "Voice-optimized latency", d: "Sub-second responses critical for real-time phone conversations" },
  { t: "Cost efficiency", d: "10x cheaper than Opus — scales across thousands of member calls" },
  { t: "Guardrail compliance", d: "System prompt constrains: no diagnoses, warm tone, short replies" },
  { t: "Dual deployment", d: "Python SDK (FastAPI) + raw HTTPS (Twilio Functions JS)" },
];
reasons.forEach((r, i) => {
  const ry = 2.25 + i * 0.65;
  s3.addShape(pres.shapes.OVAL, {
    x: 5.85, y: ry + 0.05, w: 0.22, h: 0.22,
    fill: { color: C.teal },
  });
  s3.addText(r.t, {
    x: 6.2, y: ry, w: 3.2, h: 0.25,
    fontSize: 10, fontFace: "Calibri", color: C.white, bold: true,
  });
  s3.addText(r.d, {
    x: 6.2, y: ry + 0.22, w: 3.2, h: 0.35,
    fontSize: 9, fontFace: "Calibri", color: C.gray,
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 4 — Voice Agent (Agent 1)
// ════════════════════════════════════════════════════════════════
let s4 = pres.addSlide();
s4.background = { color: C.lightBg };

s4.addText("Agent 1: Voice Care Coordinator", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.navy, bold: true,
});

// Left column — architecture
s4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 4.6, h: 3.9,
  fill: { color: C.white }, shadow: mkShadow(),
});
s4.addText("Architecture", {
  x: 0.7, y: 1.35, w: 4.2, h: 0.4,
  fontSize: 14, fontFace: "Calibri", color: C.accent, bold: true,
});

// Flow boxes
const voiceFlow = [
  { label: "Member speaks", color: C.green },
  { label: "Twilio STT", color: C.teal },
  { label: "Claude Haiku 4.5", color: C.purple },
  { label: "TTS → Speaker", color: C.green },
];
voiceFlow.forEach((f, i) => {
  const by = 1.9 + i * 0.7;
  s4.addShape(pres.shapes.RECTANGLE, {
    x: 1.2, y: by, w: 3.0, h: 0.5,
    fill: { color: f.color, transparency: 85 },
    line: { color: f.color, width: 1.5 },
  });
  s4.addText(f.label, {
    x: 1.2, y: by, w: 3.0, h: 0.5,
    fontSize: 11, fontFace: "Calibri", color: C.navy,
    bold: true, align: "center", valign: "middle",
  });
  if (i < voiceFlow.length - 1) {
    s4.addText("↓", {
      x: 2.5, y: by + 0.45, w: 0.5, h: 0.3,
      fontSize: 14, fontFace: "Calibri", color: C.gray, align: "center",
    });
  }
});

// Right column — technical details
s4.addShape(pres.shapes.RECTANGLE, {
  x: 5.3, y: 1.2, w: 4.4, h: 3.9,
  fill: { color: C.white }, shadow: mkShadow(),
});
s4.addText("Technical Details", {
  x: 5.5, y: 1.35, w: 4, h: 0.4,
  fontSize: 14, fontFace: "Calibri", color: C.accent, bold: true,
});

const voiceDetails = [
  { k: "File", v: "voice_agent.py" },
  { k: "Protocol", v: "WebSocket (Twilio ConversationRelay)" },
  { k: "Client", v: "anthropic.AsyncAnthropic (non-blocking)" },
  { k: "Max Tokens", v: "200 (brevity for voice)" },
  { k: "State", v: "In-memory conversation history per CallSid" },
  { k: "Goodbye", v: 'Detects "goodbye", "bye", "take care"' },
  { k: "Fallback", v: "Graceful error if API key missing" },
];
voiceDetails.forEach((d, i) => {
  const dy = 1.9 + i * 0.42;
  s4.addText(d.k, {
    x: 5.5, y: dy, w: 1.3, h: 0.38,
    fontSize: 9, fontFace: "Calibri", color: C.orange, bold: true, valign: "middle",
  });
  s4.addText(d.v, {
    x: 6.85, y: dy, w: 2.7, h: 0.38,
    fontSize: 9, fontFace: "Calibri", color: C.darkGray, valign: "middle",
  });
});

// System prompt box
s4.addShape(pres.shapes.RECTANGLE, {
  x: 5.3, y: 4.2, w: 4.4, h: 0.9,
  fill: { color: "FFF7ED" }, line: { color: C.orange, width: 1 },
});
s4.addText("System Prompt", {
  x: 5.5, y: 4.25, w: 2, h: 0.25,
  fontSize: 9, fontFace: "Calibri", color: C.orange, bold: true,
});
s4.addText('"Friendly Medicare care coordinator...short responses (1-3 sentences)...offer scheduling slots...never diagnose"', {
  x: 5.5, y: 4.5, w: 4, h: 0.55,
  fontSize: 8, fontFace: "Calibri", color: C.darkGray, italic: true,
});

// ════════════════════════════════════════════════════════════════
// SLIDE 5 — Message AI (Agent 2)
// ════════════════════════════════════════════════════════════════
let s5 = pres.addSlide();
s5.background = { color: C.lightBg };

s5.addText("Agent 2: Outreach Message Generator", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.navy, bold: true,
});
s5.addText("Generates personalized SMS, Email, and Call scripts per member, measure, and channel", {
  x: 0.6, y: 0.9, w: 9, h: 0.35,
  fontSize: 12, fontFace: "Calibri", color: C.darkGray,
});

// Three channel cards
const channels = [
  {
    name: "SMS", color: C.green,
    constraints: "160-character hard limit\nGreets by first name\nClear CTA: Reply YES or call\nNo emoji, no markdown, no PHI",
  },
  {
    name: "Email", color: C.accent,
    constraints: '140-word max\nSubject + body generated\n"Dear [first name]" opener\n3 action methods offered\nCloses: "Warm regards, Plan Care Team"',
  },
  {
    name: "Call Script", color: C.purple,
    constraints: "2-3 sentences\nWarm greeting + measure context\nOpen question for scheduling\nCoaching for call center agent",
  },
];
channels.forEach((ch, i) => {
  const cx = 0.5 + i * 3.15;
  s5.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: 1.45, w: 2.95, h: 2.8,
    fill: { color: C.white }, shadow: mkShadow(),
  });
  s5.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: 1.45, w: 2.95, h: 0.55,
    fill: { color: ch.color },
  });
  s5.addText(ch.name, {
    x: cx, y: 1.45, w: 2.95, h: 0.55,
    fontSize: 16, fontFace: "Calibri", color: C.white, bold: true,
    align: "center", valign: "middle",
  });
  s5.addText(ch.constraints, {
    x: cx + 0.2, y: 2.15, w: 2.55, h: 1.9,
    fontSize: 10, fontFace: "Calibri", color: C.darkGray,
    lineSpacingMultiple: 1.3,
  });
});

// Bottom: Technical implementation bar
s5.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.5, w: 9.1, h: 0.9,
  fill: { color: C.cardBg }, shadow: mkShadow(),
});
const techItems = [
  { k: "File", v: "message_ai.py" },
  { k: "Model", v: "Claude Haiku 4.5 (400 max tokens)" },
  { k: "Caching", v: "1-hour TTL, keyed by input hash" },
  { k: "Fallback", v: "Hardcoded templates on any failure" },
];
techItems.forEach((t, i) => {
  const tx = 0.7 + i * 2.25;
  s5.addText(t.k, {
    x: tx, y: 4.55, w: 2, h: 0.3,
    fontSize: 9, fontFace: "Calibri", color: C.orange, bold: true,
  });
  s5.addText(t.v, {
    x: tx, y: 4.8, w: 2, h: 0.4,
    fontSize: 9, fontFace: "Calibri", color: C.bodyText,
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 6 — Twilio Functions Agent (Agent 3)
// ════════════════════════════════════════════════════════════════
let s6 = pres.addSlide();
s6.background = { color: C.darkBg };

s6.addText("Agent 3: Twilio Serverless AI Agent", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.white, bold: true,
});
s6.addText("Claude runs directly inside Twilio Functions — bypasses Databricks OAuth (401) for webhook handling", {
  x: 0.6, y: 0.9, w: 9, h: 0.35,
  fontSize: 12, fontFace: "Calibri", color: C.ice,
});

// Architecture comparison: two columns
// Left: Why serverless?
s6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.5, w: 4.4, h: 3.5,
  fill: { color: C.cardBg }, shadow: mkShadow(),
});
s6.addText("Why Twilio Functions?", {
  x: 0.7, y: 1.6, w: 4, h: 0.4,
  fontSize: 14, fontFace: "Calibri", color: C.teal, bold: true,
});
const whyItems = [
  "Databricks Apps blocks external POST → 401 Unauthorized",
  "Twilio Functions = public endpoints, no auth barrier",
  "Node.js runtime with native Twilio SDK (twiml.VoiceResponse)",
  "ANTHROPIC_API_KEY stored as Twilio env variable",
  "Direct HTTPS call to api.anthropic.com/v1/messages",
  "In-memory conversation state (max 30 sessions)",
  "Automatic goodbye detection + session cleanup",
];
whyItems.forEach((item, i) => {
  s6.addShape(pres.shapes.OVAL, {
    x: 0.8, y: 2.15 + i * 0.4, w: 0.15, h: 0.15,
    fill: { color: C.teal },
  });
  s6.addText(item, {
    x: 1.1, y: 2.1 + i * 0.4, w: 3.6, h: 0.35,
    fontSize: 9, fontFace: "Calibri", color: C.bodyText,
  });
});

// Right: Three functions
s6.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.5, w: 4.5, h: 3.5,
  fill: { color: C.cardBg }, shadow: mkShadow(),
});
s6.addText("Deployed Functions", {
  x: 5.4, y: 1.6, w: 4, h: 0.4,
  fontSize: 14, fontFace: "Calibri", color: C.orange, bold: true,
});

const funcs = [
  { name: "/call-gather", desc: "DTMF router — Press 1 (schedule) or Press 2 (AI agent)", color: C.accent },
  { name: "/call-slot", desc: "Time slot selection — 4 options with DB logging", color: C.green },
  { name: "/call-agent", desc: "Speech → Claude → TwiML loop with conversation memory", color: C.purple },
];
funcs.forEach((f, i) => {
  const fy = 2.15 + i * 1.0;
  s6.addShape(pres.shapes.RECTANGLE, {
    x: 5.4, y: fy, w: 4.1, h: 0.85,
    fill: { color: f.color, transparency: 90 },
    line: { color: f.color, width: 1 },
  });
  s6.addText(f.name, {
    x: 5.6, y: fy + 0.05, w: 3.7, h: 0.3,
    fontSize: 11, fontFace: "Consolas", color: f.color, bold: true,
  });
  s6.addText(f.desc, {
    x: 5.6, y: fy + 0.4, w: 3.7, h: 0.35,
    fontSize: 9, fontFace: "Calibri", color: C.gray,
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 7 — System Prompts Deep Dive
// ════════════════════════════════════════════════════════════════
let s7 = pres.addSlide();
s7.background = { color: C.lightBg };

s7.addText("System Prompts — Guardrails & Persona", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.navy, bold: true,
});
s7.addText("Consistent care coordinator persona across all three LLM agents with channel-specific constraints", {
  x: 0.6, y: 0.9, w: 9, h: 0.35,
  fontSize: 12, fontFace: "Calibri", color: C.darkGray,
});

// Core persona box
s7.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.5, w: 9.1, h: 1.3,
  fill: { color: C.white }, shadow: mkShadow(),
});
s7.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.5, w: 0.08, h: 1.3, fill: { color: C.accent },
});
s7.addText("Core Persona (shared)", {
  x: 0.8, y: 1.55, w: 3, h: 0.3,
  fontSize: 12, fontFace: "Calibri", color: C.accent, bold: true,
});
s7.addText(
  '"Friendly and professional Medicare care coordinator for StarPulse. ' +
  'Warm, empathetic, helpful. Help members understand why screening/medication adherence matters. ' +
  'Assist with scheduling (tomorrow 9 AM, 2 PM, Friday 10 AM). ' +
  'Never provide specific medical diagnoses — recommend speaking with their doctor."',
  {
    x: 0.8, y: 1.9, w: 8.6, h: 0.75,
    fontSize: 10, fontFace: "Calibri", color: C.darkGray, italic: true,
    lineSpacingMultiple: 1.25,
  }
);

// Channel-specific constraints
const promptCards = [
  {
    title: "Voice Agent", color: C.accent,
    rules: [
      "1-3 sentences max",
      "End gracefully when satisfied",
      "No PHI or diagnoses",
      "Offer 3 time slots",
    ],
  },
  {
    title: "SMS Generator", color: C.green,
    rules: [
      "160-character hard limit",
      "Greet by first name",
      "CTA: Reply YES or call",
      "No emoji / markdown",
    ],
  },
  {
    title: "Email Generator", color: C.teal,
    rules: [
      "140-word maximum",
      "Subject line generated",
      '"Dear [Name]" opener',
      "3 action methods (call/reply/portal)",
    ],
  },
  {
    title: "Call Script", color: C.purple,
    rules: [
      "2-3 sentences",
      "Coaching for agent",
      "Measure context included",
      "Open scheduling question",
    ],
  },
];
promptCards.forEach((pc, i) => {
  const cx = 0.5 + i * 2.35;
  s7.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: 3.05, w: 2.15, h: 2.3,
    fill: { color: C.white }, shadow: mkShadow(),
  });
  s7.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: 3.05, w: 2.15, h: 0.45,
    fill: { color: pc.color },
  });
  s7.addText(pc.title, {
    x: cx, y: 3.05, w: 2.15, h: 0.45,
    fontSize: 11, fontFace: "Calibri", color: C.white, bold: true,
    align: "center", valign: "middle",
  });
  pc.rules.forEach((rule, j) => {
    s7.addShape(pres.shapes.OVAL, {
      x: cx + 0.15, y: 3.68 + j * 0.38, w: 0.12, h: 0.12,
      fill: { color: pc.color },
    });
    s7.addText(rule, {
      x: cx + 0.35, y: 3.62 + j * 0.38, w: 1.65, h: 0.32,
      fontSize: 9, fontFace: "Calibri", color: C.darkGray,
    });
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 8 — ML Models: Propensity & Urgency
// ════════════════════════════════════════════════════════════════
let s8 = pres.addSlide();
s8.background = { color: C.darkBg };

s8.addText("ML Models — Predictive Analytics", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.white, bold: true,
});

// Left: Propensity model
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 4.5, h: 4.0,
  fill: { color: C.cardBg }, shadow: mkShadow(),
});
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 4.5, h: 0.55,
  fill: { color: C.green },
});
s8.addText("Gap Closure Propensity Model", {
  x: 0.7, y: 1.2, w: 4, h: 0.55,
  fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, valign: "middle",
});

const propDetails = [
  ["Algorithm", "GradientBoostingClassifier (sklearn)"],
  ["Purpose", "Predict probability member closes an open gap"],
  ["Output Table", "gold_member_closure_propensity"],
  ["Score Range", "0.0 — 1.0 (probability)"],
  ["Notebook", "15_ml_closure_propensity.py"],
];
propDetails.forEach((row, i) => {
  const ry = 1.95 + i * 0.45;
  s8.addText(row[0], {
    x: 0.7, y: ry, w: 1.5, h: 0.4,
    fontSize: 10, fontFace: "Calibri", color: C.green, bold: true, valign: "middle",
  });
  s8.addText(row[1], {
    x: 2.2, y: ry, w: 2.6, h: 0.4,
    fontSize: 10, fontFace: "Calibri", color: C.bodyText, valign: "middle",
  });
});

// Features list
s8.addText("Input Features", {
  x: 0.7, y: 4.15, w: 4, h: 0.3,
  fontSize: 10, fontFace: "Calibri", color: C.orange, bold: true,
});
s8.addText("age, utilization_segment, dual_eligible, LIS flag, comorbidity count, claims history, channel, incentive", {
  x: 0.7, y: 4.4, w: 4, h: 0.55,
  fontSize: 9, fontFace: "Calibri", color: C.gray,
});

// Right: HOS Urgency model
s8.addShape(pres.shapes.RECTANGLE, {
  x: 5.3, y: 1.2, w: 4.4, h: 4.0,
  fill: { color: C.cardBg }, shadow: mkShadow(),
});
s8.addShape(pres.shapes.RECTANGLE, {
  x: 5.3, y: 1.2, w: 4.4, h: 0.55,
  fill: { color: C.orange },
});
s8.addText("HOS Fall-Risk Urgency Model", {
  x: 5.5, y: 1.2, w: 4, h: 0.55,
  fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, valign: "middle",
});

const hosDetails = [
  ["Algorithm", "RandomForestRegressor (sklearn)"],
  ["Purpose", "Predict urgency score for HOS fall-risk members"],
  ["Output Table", "gold_hos_members.urgency_score"],
  ["Score Range", "15 — 98"],
  ["Notebook", "16_ml_hos_urgency.py"],
];
hosDetails.forEach((row, i) => {
  const ry = 1.95 + i * 0.45;
  s8.addText(row[0], {
    x: 5.5, y: ry, w: 1.5, h: 0.4,
    fontSize: 10, fontFace: "Calibri", color: C.orange, bold: true, valign: "middle",
  });
  s8.addText(row[1], {
    x: 7.0, y: ry, w: 2.5, h: 0.4,
    fontSize: 10, fontFace: "Calibri", color: C.bodyText, valign: "middle",
  });
});

// Feature weights
s8.addText("Feature Weights", {
  x: 5.5, y: 4.15, w: 4, h: 0.3,
  fontSize: 10, fontFace: "Calibri", color: C.teal, bold: true,
});
const featureWeights = [
  { name: "fall_history_severity", pct: 25 },
  { name: "awv_status", pct: 20 },
  { name: "age", pct: 15 },
  { name: "comorbidities", pct: 15 },
];
featureWeights.forEach((fw, i) => {
  const fx = 5.5 + i * 1.05;
  s8.addText(`${fw.name}\n${fw.pct}%`, {
    x: fx, y: 4.4, w: 1.0, h: 0.6,
    fontSize: 8, fontFace: "Calibri", color: C.gray, align: "center",
  });
  // Mini bar
  s8.addShape(pres.shapes.RECTANGLE, {
    x: fx + 0.15, y: 4.95, w: 0.7 * (fw.pct / 25), h: 0.08,
    fill: { color: C.teal },
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 9 — Data Flow: Models ↔ Platform
// ════════════════════════════════════════════════════════════════
let s9 = pres.addSlide();
s9.background = { color: C.lightBg };

s9.addText("End-to-End AI Data Flow", {
  x: 0.6, y: 0.3, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Calibri", color: C.navy, bold: true,
});

// Flow: Left to Right pipeline
const pipeline = [
  { label: "Member Data\n(Databricks Silver)", w: 1.8, color: C.teal, y: 2.0 },
  { label: "ML Scoring\n(Gold Tables)", w: 1.6, color: C.green, y: 2.0 },
  { label: "Campaign\nSelection", w: 1.4, color: C.accent, y: 2.0 },
  { label: "Claude AI\nMessage Gen", w: 1.6, color: C.purple, y: 2.0 },
  { label: "Multi-Channel\nDelivery", w: 1.6, color: C.orange, y: 2.0 },
];
let px = 0.4;
pipeline.forEach((p, i) => {
  s9.addShape(pres.shapes.RECTANGLE, {
    x: px, y: p.y, w: p.w, h: 1.1,
    fill: { color: p.color, transparency: 85 },
    line: { color: p.color, width: 2 },
    shadow: mkShadow(),
  });
  s9.addText(p.label, {
    x: px, y: p.y, w: p.w, h: 1.1,
    fontSize: 10, fontFace: "Calibri", color: C.navy,
    bold: true, align: "center", valign: "middle",
  });
  if (i < pipeline.length - 1) {
    s9.addText("→", {
      x: px + p.w, y: p.y, w: 0.35, h: 1.1,
      fontSize: 20, fontFace: "Calibri", color: C.gray,
      align: "center", valign: "middle",
    });
    px += p.w + 0.35;
  } else {
    px += p.w;
  }
});

// Bottom: detail boxes for each stage
const details = [
  { title: "Ingest", desc: "Demographics, claims,\nHEDIS gaps, HOS surveys", color: C.teal },
  { title: "Score", desc: "Propensity (0-1)\nUrgency (15-98)\nPriority ranking", color: C.green },
  { title: "Target", desc: "Gap-based filtering\nChannel preference\nRound-robin contacts", color: C.accent },
  { title: "Generate", desc: "Per-member personalization\nChannel-specific prompts\n1-hr cached responses", color: C.purple },
  { title: "Deliver", desc: "Twilio (SMS + Voice)\nSendGrid (Email)\nAudit → Databricks", color: C.orange },
];
details.forEach((d, i) => {
  const dx = 0.4 + i * 1.9;
  s9.addShape(pres.shapes.RECTANGLE, {
    x: dx, y: 3.4, w: 1.7, h: 1.7,
    fill: { color: C.white }, shadow: mkShadow(),
  });
  s9.addShape(pres.shapes.RECTANGLE, {
    x: dx, y: 3.4, w: 1.7, h: 0.06, fill: { color: d.color },
  });
  s9.addText(d.title, {
    x: dx + 0.1, y: 3.5, w: 1.5, h: 0.35,
    fontSize: 11, fontFace: "Calibri", color: d.color, bold: true,
  });
  s9.addText(d.desc, {
    x: dx + 0.1, y: 3.85, w: 1.5, h: 1.1,
    fontSize: 9, fontFace: "Calibri", color: C.darkGray,
    lineSpacingMultiple: 1.3,
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 10 — Metrics & Evaluation
// ════════════════════════════════════════════════════════════════
let s10 = pres.addSlide();
s10.background = { color: C.darkBg };

s10.addText("Model Evaluation & Metrics", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.white, bold: true,
});

// ML Metrics table
s10.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 9.1, h: 0.5,
  fill: { color: C.accent },
});
s10.addText("ML Model Metrics", {
  x: 0.7, y: 1.2, w: 3, h: 0.5,
  fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, valign: "middle",
});

const metricHeaders = ["Model", "Metric", "Purpose", "Evaluation Method"];
metricHeaders.forEach((h, i) => {
  const hx = 0.5 + i * 2.275;
  s10.addText(h, {
    x: hx, y: 1.75, w: 2.275, h: 0.4,
    fontSize: 10, fontFace: "Calibri", color: C.orange, bold: true, valign: "middle",
  });
});
const metricRows = [
  ["Propensity", "ROC-AUC", "Discrimination ability", "Train/test split (80/20)"],
  ["Propensity", "Avg Precision", "Precision-recall tradeoff", "sklearn metrics"],
  ["Propensity", "Brier Score", "Calibration accuracy", "Predicted vs actual probs"],
  ["HOS Urgency", "MAE", "Prediction error", "Mean Absolute Error"],
  ["HOS Urgency", "MSE", "Variance sensitivity", "Mean Squared Error"],
];
metricRows.forEach((row, i) => {
  const ry = 2.2 + i * 0.42;
  s10.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: ry, w: 9.1, h: 0.4,
    fill: { color: i % 2 === 0 ? "1A2744" : "15203A" },
  });
  row.forEach((cell, j) => {
    s10.addText(cell, {
      x: 0.5 + j * 2.275, y: ry, w: 2.275, h: 0.4,
      fontSize: 10, fontFace: "Calibri", color: C.bodyText, valign: "middle",
    });
  });
});

// LLM Quality section
s10.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.1, w: 9.1, h: 0.5,
  fill: { color: C.purple },
});
s10.addText("LLM Quality Controls", {
  x: 0.7, y: 4.1, w: 3, h: 0.5,
  fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, valign: "middle",
});

const llmControls = [
  { label: "Token Limits", desc: "200 (voice) / 400 (msg)" },
  { label: "Response Caching", desc: "1-hr TTL, hash-keyed" },
  { label: "Fallback Templates", desc: "Hardcoded if API fails" },
  { label: "Audit Logging", desc: "Every turn → Databricks" },
];
llmControls.forEach((lc, i) => {
  const lx = 0.5 + i * 2.275;
  s10.addText(lc.label, {
    x: lx, y: 4.65, w: 2.275, h: 0.3,
    fontSize: 10, fontFace: "Calibri", color: C.teal, bold: true,
  });
  s10.addText(lc.desc, {
    x: lx, y: 4.9, w: 2.275, h: 0.3,
    fontSize: 9, fontFace: "Calibri", color: C.gray,
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 11 — Safety & Compliance
// ════════════════════════════════════════════════════════════════
let s11 = pres.addSlide();
s11.background = { color: C.lightBg };

s11.addText("AI Safety & Compliance", {
  x: 0.6, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Calibri", color: C.navy, bold: true,
});

const safetyCards = [
  {
    title: "No Medical Diagnoses",
    desc: "System prompt explicitly prohibits diagnostic statements. Claude redirects to PCP for all clinical questions.",
    color: "DC2626",
  },
  {
    title: "No PHI in Prompts",
    desc: "Only first name, measure, and age sent to Claude. No SSN, MBI, claims, or addresses in LLM context.",
    color: C.orange,
  },
  {
    title: "Graceful Degradation",
    desc: "If Anthropic API is unreachable, system falls back to pre-approved hardcoded templates — never fails silently.",
    color: C.accent,
  },
  {
    title: "Full Audit Trail",
    desc: "Every AI interaction logged to Databricks: member speech, AI response, timestamps, status transitions.",
    color: C.green,
  },
  {
    title: "Token Budget Control",
    desc: "Max 200 tokens for voice (prevents monologues), 400 for messages. Prevents runaway costs and verbose output.",
    color: C.purple,
  },
  {
    title: "Session Isolation",
    desc: "Per-CallSid conversation memory. Auto-cleanup after goodbye. Max 30/50 concurrent sessions.",
    color: C.teal,
  },
];
safetyCards.forEach((sc, i) => {
  const row = Math.floor(i / 3);
  const col = i % 3;
  const cx = 0.5 + col * 3.15;
  const cy = 1.2 + row * 2.0;
  s11.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 2.95, h: 1.8,
    fill: { color: C.white }, shadow: mkShadow(),
  });
  s11.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 0.08, h: 1.8, fill: { color: sc.color },
  });
  s11.addText(sc.title, {
    x: cx + 0.2, y: cy + 0.15, w: 2.55, h: 0.4,
    fontSize: 12, fontFace: "Calibri", color: C.navy, bold: true,
  });
  s11.addText(sc.desc, {
    x: cx + 0.2, y: cy + 0.6, w: 2.55, h: 1.0,
    fontSize: 10, fontFace: "Calibri", color: C.darkGray,
    lineSpacingMultiple: 1.25,
  });
});

// ════════════════════════════════════════════════════════════════
// SLIDE 12 — Thank You
// ════════════════════════════════════════════════════════════════
let s12 = pres.addSlide();
s12.background = { color: C.darkBg };

s12.addText("EXL  |  StarPulse", {
  x: 0.8, y: 1.0, w: 8, h: 0.5,
  fontSize: 14, fontFace: "Calibri", color: C.orange,
  charSpacing: 4, bold: true,
});
s12.addText("Thank You", {
  x: 0.8, y: 1.8, w: 8, h: 1.2,
  fontSize: 48, fontFace: "Calibri", color: C.white, bold: true,
});
s12.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 3.2, w: 1.5, h: 0.06, fill: { color: C.orange },
});
s12.addText("3 LLM Agents  +  2 ML Models  +  Full Audit Trail", {
  x: 0.8, y: 3.5, w: 8, h: 0.5,
  fontSize: 16, fontFace: "Calibri", color: C.ice,
});
s12.addText("Built on Claude Haiku 4.5  |  scikit-learn  |  Twilio  |  Databricks", {
  x: 0.8, y: 4.1, w: 8, h: 0.4,
  fontSize: 12, fontFace: "Calibri", color: C.gray,
});

// ── Save ──
const outPath = "C:\\STARS_FInal_Draft\\StarPulse_Models_Agents.pptx";
pres.writeFile({ fileName: outPath }).then(() => {
  console.log("Saved:", outPath);
});
