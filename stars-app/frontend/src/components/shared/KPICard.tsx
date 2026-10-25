interface KPICardProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: "red" | "teal" | "amber" | "blue";
}

export default function KPICard({ label, value, sub, color = "teal" }: KPICardProps) {
  return (
    <div className={`kpi ${color}`}>
      <div className="text-muted text-xs mb-1">{label}</div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {sub && <div className="text-muted text-xs mt-1">{sub}</div>}
    </div>
  );
}
