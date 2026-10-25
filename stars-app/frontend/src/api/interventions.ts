import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";

export interface InterventionRow {
  intervention_id: string;
  intervention_name: string;
  measure_code: string;
  measure_name: string;
  owner_department: string;
  expected_lift_pct: number;
  status: string;
  due_date: string;
  member_count: number;
}

export function useGetInterventions() {
  return useQuery<InterventionRow[]>({
    queryKey: ["interventions"],
    queryFn: () => apiFetch("/api/interventions"),
    staleTime: 5 * 60 * 1000,
  });
}
