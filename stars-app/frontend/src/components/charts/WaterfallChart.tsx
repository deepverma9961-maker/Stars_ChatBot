import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import type { WaterfallWeek } from "../../types/simulator";
import { COLORS } from "../../styles/tokens";

export default function WaterfallChart({ data }: { data: WaterfallWeek[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2d3e52" />
        <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis yAxisId="left" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fill: "#94a3b8", fontSize: 11 }} domain={[60, 100]} />
        <Tooltip
          contentStyle={{ background: "#1e2a3a", border: "1px solid #2d3e52", borderRadius: 8 }}
          labelStyle={{ color: "#fff" }}
          itemStyle={{ color: "#94a3b8" }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
        <Bar yAxisId="left" dataKey="outreach_count" name="Outreach" fill={COLORS.blue} opacity={0.7} radius={[3,3,0,0]} />
        <Bar yAxisId="left" dataKey="estimated_closures" name="Closures" fill={COLORS.teal} opacity={0.9} radius={[3,3,0,0]} />
        <Line yAxisId="right" type="monotone" dataKey="cumulative_compliance" name="Compliance %" stroke={COLORS.amber} strokeWidth={2} dot={{ r: 4, fill: COLORS.amber }} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
