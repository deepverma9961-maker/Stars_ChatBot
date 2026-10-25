interface ProgressBarProps {
  value: number;       // current %
  target?: number;     // target % for marker
  status?: string;
  showLabel?: boolean;
}

export default function ProgressBar({ value, target, status = "green", showLabel = false }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, value));
  const tPct = target ? Math.min(100, Math.max(0, target)) : null;
  return (
    <div className="flex items-center gap-2">
      {showLabel && <span className="text-xs text-muted w-10 text-right">{value.toFixed(1)}%</span>}
      <div className="progress-bar flex-1">
        <div className={`progress-fill ${status}`} style={{ width: `${pct}%` }} />
        {tPct !== null && (
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-white/40"
            style={{ left: `${tPct}%` }}
          />
        )}
      </div>
    </div>
  );
}
