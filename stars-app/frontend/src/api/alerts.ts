import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { AlertsResponse } from "../types/alert";

export function useGetAlerts() {
  return useQuery<AlertsResponse>({
    queryKey: ["alerts"],
    queryFn: () => apiFetch("/api/alerts"),
    staleTime: 2 * 60 * 1000,
  });
}
