import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";

export interface TeamViewRow {
  department: string;
  leader: string;
  measures_owned: string[];
  on_track_count: number;
  at_risk_count: number;
  critical_count: number;
  action_status: string;
  next_action: string;
}

export function useGetTeamView() {
  return useQuery<TeamViewRow[]>({
    queryKey: ["team-view"],
    queryFn: () => apiFetch("/api/team-view"),
    staleTime: 5 * 60 * 1000,
  });
}
