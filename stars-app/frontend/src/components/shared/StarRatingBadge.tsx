import { STAR_CLASS } from "../../styles/tokens";

interface StarRatingBadgeProps {
  rating: number;
  size?: "sm" | "md" | "lg";
}

export default function StarRatingBadge({ rating, size = "md" }: StarRatingBadgeProps) {
  const key = String(rating);
  const cls = STAR_CLASS[key] ?? "s4";
  const sizeCls = size === "lg" ? "text-lg px-3 py-1" : size === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-0.5";
  return (
    <span className={`star-badge ${cls} ${sizeCls}`}>
      {rating.toFixed(1)}
    </span>
  );
}
