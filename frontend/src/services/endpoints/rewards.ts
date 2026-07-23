import { apiClient } from "@/services/apiClient";
import type { Paginated, PlayerMission, ShopItem } from "@/types/api";

export async function listPlayerMissions(): Promise<PlayerMission[]> {
  const { data } = await apiClient.get<Paginated<PlayerMission>>("/rewards/player-missions/", {
    params: { page_size: 20 },
  });
  return data.results;
}

export async function claimMission(id: string): Promise<{ xp_awarded: number; coin_awarded: number }> {
  const { data } = await apiClient.post(`/rewards/player-missions/${id}/claim/`);
  return data;
}

export async function listShopItems(): Promise<ShopItem[]> {
  const { data } = await apiClient.get<Paginated<ShopItem>>("/rewards/shop-items/", { params: { page_size: 50 } });
  return data.results;
}

export async function purchaseItem(shopItemId: string) {
  const { data } = await apiClient.post("/rewards/purchases/", { shop_item_id: shopItemId });
  return data;
}
