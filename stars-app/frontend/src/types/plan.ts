export interface PlanSummary {
  contract_id: string;
  plan_name: string;
  state: string;
  enrollment: number;
  py_rating: number;
  projected_rating: number;
  hedis_rating: number;
  cahps_rating: number;
  hos_rating: number;
  partd_rating: number;
  star_gap_to_4: number;
  bonus_eligible: boolean;
}

export interface DomainScore {
  domain: string;
  rating: number;
  on_track_count: number;
  total_count: number;
  critical_count: number;
}

export interface HistoricalRating {
  year: string;
  rating: number;
}

export interface PlanDetail extends PlanSummary {
  historical_ratings: HistoricalRating[];
  domain_scores: DomainScore[];
}

export interface StarSummary {
  total_plans: number;
  total_enrollment: number;
  above_4star_count: number;
  above_4star_pct: number;
  avg_star_rating: number;
  measurement_year: number;
}
