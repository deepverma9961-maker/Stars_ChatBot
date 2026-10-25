import type { Channel, Incentive, GapStatus, PropensityTier } from "./common";

export interface SimulatorConfig {
  contract_id: string;
  measure_code: string | null;
  gap_statuses: GapStatus[];
  propensity_tiers: PropensityTier[];
  channels: Channel[];
  incentive: Incentive;
  suppressions: {
    recently_contacted: boolean;
    opted_out: boolean;
    already_closed: boolean;
  };
}

export interface WaterfallWeek {
  label: string;
  outreach_count: number;
  estimated_closures: number;
  cumulative_compliance: number;
}

export interface SegmentRow {
  label: string;
  members: number;
  channel: string;
  incentive: string;
  estimated_closures: number;
  closure_rate_pct: number;
  estimated_cost: number;
}

export interface SimulatorResult {
  net_pool: number;
  estimated_closures: number;
  projected_rate: number;
  lift: number;
  eligible_members: number;
  measure_name: string;
  measure_pct: number;
  channel_mix: Record<string, number>;
  waterfall: WaterfallWeek[];
  segments: SegmentRow[];
}
