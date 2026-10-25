export const COLORS = {
  red: "#F26722",
  teal: "#1D9E75",
  amber: "#d97706",
  navy: "#1e293b",
  dark: "#0f172a",
  card: "#1e2a3a",
  border: "#2d3e52",
  green: "#059669",
  blue: "#3b82f6",
} as const;

export const STATUS_COLOR: Record<string, string> = {
  green: COLORS.teal,
  yellow: COLORS.amber,
  red: COLORS.red,
};

export const CHANNEL_CLASS: Record<string, string> = {
  Call: "ch-call",
  SMS: "ch-sms",
  Email: "ch-email",
  Portal: "ch-portal",
};

export const STAR_CLASS: Record<string, string> = {
  "5": "s5",
  "4.5": "s45",
  "4": "s4",
  "3.5": "s35",
  "3": "s3",
};
