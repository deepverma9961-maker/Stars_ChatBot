import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import type { CahpsComposite } from "../../types/cahps";
import { COLORS } from "../../styles/tokens";

export default function CahpsBarChart({ composites }: { composites: CahpsComposite[] }) {
  const data = composites.map(c => ({
    name: c.composite_name.split(" ").slice(0, 2).join(" "),
    value: c.current_pct,
    fill: c.status === "ok" ? COLORS.teal : c.status === "risk" ? COLORS.amber : COLORS.red,
  }));
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 4, right: 8, bottom: 24, left: 0 }} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#2d3e52" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis type="category" dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} width={90} />
        <Tooltip
          contentStyle={{ background: "#1e2a3a", border: "1px solid #2d3e52", borderRadius: 8 }}
          formatter={(v: number) => [`${v.toFixed(1)}%`, "Score"]}
        />
        <ReferenceLine x={80} stroke="#ffffff30" strokeDasharray="4 4" />
        <Bar dataKey="value" radius={[0, 3, 3, 0]}>
          {data.map((d, i) => (
            <rect key={i} fill={d.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
