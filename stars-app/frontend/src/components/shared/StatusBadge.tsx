interface StatusBadgeProps {
  status: string;
  label?: string;
}

const MAP: Record<string, string> = {
  green: "green", yellow: "yellow", red: "red",
  ok: "green", risk: "yellow", crit: "red", critical: "red",
  Active: "teal", Completed: "green", Planned: "blue",
  "In Progress": "amber", "Not Started": "gray",
};

export default function StatusBadge({ status, label }: StatusBadgeProps) {
  const color = MAP[status] ?? "gray";
  return <span className={`pill ${color}`}>{label ?? status}</span>;
}
