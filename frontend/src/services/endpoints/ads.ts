import { apiClient } from "@/services/apiClient";

interface AdRewardResult {
  coins_awarded: number;
  coins: number;
}

/** A appeler apres qu'une pub recompensee a ete regardee jusqu'au bout (voir lib/ads.ts). */
export async function claimAdReward(): Promise<AdRewardResult> {
  const { data } = await apiClient.post<AdRewardResult>("/auth/me/claim-ad-reward/");
  return data;
}
