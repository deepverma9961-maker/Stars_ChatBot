import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { PlanSummary, PlanDetail } from "../types/plan";

export interface PlanFilters {
  state?: string;
  py_rating?: number;
  proj_rating?: number;
  search?: string;
}

export function useGetPlans(filters: PlanFilters = {}) {
  const params = new URLSearchParams();
  if (filters.state) params.set("state", filters.state);
  if (filters.py_rating) params.set("py_rating", String(filters.py_rating));
  if (filters.proj_rating) params.set("proj_rating", String(filters.proj_rating));
  if (filters.search) params.set("search", filters.search);
  const qs = params.toString();
  return useQuery<PlanSummary[]>({
    queryKey: ["plans", filters],
    queryFn: () => apiFetch(`/api/plans${qs ? "?" + qs : ""}`),
    staleTime: 5 * 60 * 1000,
  });
}

export function useGetPlanDetail(contractId: string) {
  return useQuery<PlanDetail>({
    queryKey: ["plan", contractId],
    queryFn: () => apiFetch(`/api/plans/${contractId}`),
    staleTime: 5 * 60 * 1000,
    enabled: !!contractId,
  });
}
