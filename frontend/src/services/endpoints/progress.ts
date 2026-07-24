import { apiClient } from "@/services/apiClient";
import type { CompleteLevelResult, Paginated, PlayerProgress, StakeLevelResult } from "@/types/api";

export async function listProgress(): Promise<PlayerProgress[]> {
  const { data } = await apiClient.get<Paginated<PlayerProgress>>("/progress/entries/", { params: { page_size: 20 } });
  return data.results;
}

export async function completeLevel(levelId: string, scorePercent: number): Promise<CompleteLevelResult> {
  const { data } = await apiClient.post<CompleteLevelResult>("/progress/entries/complete-level/", {
    level_id: levelId,
    score_percent: scorePercent,
  });
  return data;
}

export async function stakeLevel(levelId: string): Promise<StakeLevelResult> {
  const { data } = await apiClient.post<StakeLevelResult>("/progress/entries/stake-level/", {
    level_id: levelId,
  });
  return data;
}
