import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { StarSummary } from "../types/plan";

export function useGetStarSummary() {
  return useQuery<StarSummary>({
    queryKey: ["star-summary"],
    queryFn: () => apiFetch("/api/star-summary"),
    staleTime: 5 * 60 * 1000,
  });
}
