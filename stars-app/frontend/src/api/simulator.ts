import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { SimulatorConfig, SimulatorResult } from "../types/simulator";

export function useRunSimulator() {
  return useMutation<SimulatorResult, Error, SimulatorConfig>({
    mutationFn: (config) =>
      apiFetch("/api/simulator/run", { method: "POST", body: JSON.stringify(config) }),
  });
}
