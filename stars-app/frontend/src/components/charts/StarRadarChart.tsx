import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";
import type { DomainScore } from "../../types/plan";
import { COLORS } from "../../styles/tokens";

export default function StarRadarChart({ domains }: { domains: DomainScore[] }) {
  const data = domains.map(d => ({ subject: d.domain, value: d.rating, fullMark: 5 }));
  return (
    <ResponsiveContainer width="100%" height={200}>
      <RadarChart data={data}>
        <PolarGrid stroke="#2d3e52" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Radar dataKey="value" stroke={COLORS.teal} fill={COLORS.teal} fillOpacity={0.3} dot />
        <Tooltip
          contentStyle={{ background: "#1e2a3a", border: "1px solid #2d3e52", borderRadius: 8 }}
          formatter={(v: number) => [`${v.toFixed(1)} ★`, "Rating"]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
