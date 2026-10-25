import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import type { HistoricalRating } from "../../types/plan";
import { COLORS } from "../../styles/tokens";

export default function ComplianceLineChart({ data, target = 4.0 }: { data: HistoricalRating[]; target?: number }) {
  return (
    <ResponsiveContainer width="100%" height={140}>
      <LineChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2d3e52" />
        <XAxis dataKey="year" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis domain={[2.5, 5.5]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <ReferenceLine y={target} stroke={COLORS.amber} strokeDasharray="4 4" label={{ value: "4★", fill: COLORS.amber, fontSize: 10 }} />
        <Tooltip
          contentStyle={{ background: "#1e2a3a", border: "1px solid #2d3e52", borderRadius: 8 }}
          formatter={(v: number) => [`${v.toFixed(1)} ★`, "Rating"]}
        />
        <Line type="monotone" dataKey="rating" stroke={COLORS.teal} strokeWidth={2} dot={{ r: 4, fill: COLORS.teal }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
