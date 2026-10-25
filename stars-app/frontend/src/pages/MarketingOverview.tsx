import { useNavigate } from "react-router-dom";

const PLATFORM_CAPS = [
  { icon: "📋", title: "HEDIS Clinical Quality",    desc: "Leverage AI to monitor HEDIS measures, pinpoint gaps, and engage members.",              link: "Explore →", page: "/hedis" },
  { icon: "👥", title: "CAHPS Member Experience",   desc: "Analyze CAHPS survey data to uncover drivers of member satisfaction.",                   link: "Explore →", page: "/cahps" },
  { icon: "❤️", title: "HOS Health Outcomes",       desc: "Track physical and mental health outcomes to support star rating goals.",                  link: "Explore →", page: "/hedis" },
  { icon: "💊", title: "Medical Adherence",          desc: "Monitor PDC-based adherence and close pharmacy gaps.",                                     link: "Explore →", page: "/simulator" },
  { icon: "🛡️", title: "Admin / Operational",       desc: "Track appeals, call center access, quality scores, and complaints.",                       link: "Explore →", page: "/executive" },
];

const QUICK_NAV = [
  { icon: "⚙️", title: "Simulator",               desc: "Model scenarios and see their impact on Star ratings in real-time.",                        link: "Launch →", page: "/simulator" },
  { icon: "🤖", title: "Agent Execution",          desc: "Manage outreach campaigns with tailored agent scripts.",                                     link: "Launch →", page: "/agent" },
  { icon: "📈", title: "Impact Projector",         desc: "Simulate closure rates and visualize the lift of reaching 4★.",                             link: "Launch →", page: "/projector" },
  { icon: "💰", title: "Campaign History & ROI",   desc: "Track campaigns, measuring performance, cost, and ROI.",                                     link: "Launch →", page: "/campaigns" },
  { icon: "⚠️", title: "Alerts & Priorities",      desc: "Stay on top of critical measure drops and prioritized action items.",                        link: "Launch →", page: "/alerts" },
];

const ORANGE = "#F26722";

const capCardStyle: React.CSSProperties = {
  padding: "12px 14px",
  borderRight: "1px solid #e5e7eb",
  cursor: "pointer",
  position: "relative",
  background: "#fff",
  transition: "background 0.15s",
};

const capIconStyle: React.CSSProperties = {
  width: "28px", height: "28px",
  background: "#fff5ef",
  borderRadius: "8px",
  display: "flex", alignItems: "center", justifyContent: "center",
  fontSize: "14px", marginBottom: "8px",
};

export default function MarketingOverview() {
  const navigate = useNavigate();

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", fontFamily: "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" }}>

      {/* ── Hero ── */}
      <div style={{
        background: "linear-gradient(135deg,#1a1a2e 0%,#2d1b14 60%,#3d2010 100%)",
        padding: "28px 32px", color: "#fff", flexShrink: 0,
      }}>
        {/* EXL logo */}
        <div style={{ marginBottom: "16px" }}>
          <span style={{ fontSize: "22px", fontWeight: 800, color: ORANGE, letterSpacing: "-0.5px" }}>EXL</span>
          <span style={{ fontSize: "13px", color: "#9ca3af", marginLeft: "10px", fontWeight: 400 }}>StarPulse · Medicare Stars Platform</span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "24px" }}>
          {/* Left */}
          <div style={{ flex: 1 }}>
            <h1 style={{ fontSize: "36px", fontWeight: 800, lineHeight: 1.15, marginBottom: "12px", letterSpacing: "-0.5px" }}>
              Close every gap.<br />
              <span style={{ color: ORANGE }}>Reach 4★ and beyond.</span>
            </h1>
            <p style={{ fontSize: "15px", color: "#9ca3af", maxWidth: "600px", lineHeight: 1.5, marginBottom: "12px" }}>
              StarPulse is an AI-powered Medicare Stars platform that identifies member gaps, automates outreach campaigns, and projects your CMS star rating — across all domains, in real time.
            </p>
          </div>

          {/* Right — Executive Overview card */}
          <div style={{
            width: "360px", flexShrink: 0,
            display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center",
            padding: "24px",
            background: "linear-gradient(135deg,#eff6ff,#dbeafe)",
            border: "1px solid #bfdbfe", borderRadius: "12px",
          }}>
            <div style={{ width: "48px", height: "48px", background: "#fff", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "24px", marginBottom: "16px" }}>📊</div>
            <div style={{ fontSize: "16px", fontWeight: 700, marginBottom: "8px", color: "#1e3a8a" }}>Executive Overview</div>
            <div style={{ fontSize: "12px", marginBottom: "16px", maxWidth: "280px", lineHeight: 1.5, color: "#3b82f6" }}>
              Monitor all top contracts by enrollment, compare PY to Projected ratings, and identify underperforming plans.
            </div>
            <button
              onClick={() => navigate("/executive")}
              style={{ padding: "10px 24px", fontSize: "13px", background: "#1d4ed8", color: "#fff", border: "none", borderRadius: "7px", fontWeight: 600, cursor: "pointer" }}
            >
              View Executive Overview →
            </button>
          </div>
        </div>
      </div>

      {/* ── Below hero (white bg) ── */}
      <div style={{ padding: "20px 24px", background: "#f5f6f8", flex: 1 }}>

        {/* Platform Capabilities */}
        <div style={{ fontSize: "10px", fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "8px" }}>
          Platform Capabilities
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 0,
          background: "#fff", border: "1px solid #e5e7eb", borderRadius: "12px",
          overflow: "hidden", marginBottom: "24px",
        }}>
          {PLATFORM_CAPS.map((c, i) => (
            <div
              key={c.title}
              onClick={() => navigate(c.page)}
              style={{ ...capCardStyle, borderRight: i === PLATFORM_CAPS.length - 1 ? "none" : "1px solid #e5e7eb" }}
              onMouseEnter={e => (e.currentTarget.style.background = "#fff8f5")}
              onMouseLeave={e => (e.currentTarget.style.background = "#fff")}
            >
              {/* top accent bar */}
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "3px", background: ORANGE }} />
              <div style={capIconStyle}>{c.icon}</div>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#111", marginBottom: "4px", lineHeight: 1.2 }}>{c.title}</div>
              <div style={{ fontSize: "11px", color: "#6b7280", lineHeight: 1.4, marginBottom: "8px" }}>{c.desc}</div>
              <div style={{ fontSize: "11px", fontWeight: 600, color: ORANGE }}>{c.link}</div>
            </div>
          ))}
        </div>

        {/* Quick Navigation */}
        <div style={{ fontSize: "10px", fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "8px" }}>
          Quick Navigation
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 0,
          background: "#fff", border: "1px solid #e5e7eb", borderRadius: "12px",
          overflow: "hidden",
        }}>
          {QUICK_NAV.map((c, i) => (
            <div
              key={c.title}
              onClick={() => navigate(c.page)}
              style={{ ...capCardStyle, borderRight: i === QUICK_NAV.length - 1 ? "none" : "1px solid #e5e7eb" }}
              onMouseEnter={e => (e.currentTarget.style.background = "#fff8f5")}
              onMouseLeave={e => (e.currentTarget.style.background = "#fff")}
            >
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "3px", background: ORANGE }} />
              <div style={capIconStyle}>{c.icon}</div>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#111", marginBottom: "4px", lineHeight: 1.2 }}>{c.title}</div>
              <div style={{ fontSize: "11px", color: "#6b7280", lineHeight: 1.4, marginBottom: "8px" }}>{c.desc}</div>
              <div style={{ fontSize: "11px", fontWeight: 600, color: ORANGE }}>{c.link}</div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
