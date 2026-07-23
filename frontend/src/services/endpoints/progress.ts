import { apiClient } from "@/services/apiClient";
import type { CompleteLevelResult, Paginated, PlayerProgress } from "@/types/api";

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
