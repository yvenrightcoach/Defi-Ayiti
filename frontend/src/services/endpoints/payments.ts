import { apiClient } from "@/services/apiClient";
import type { DiamondPack, Paginated } from "@/types/api";

export async function listDiamondPacks(): Promise<DiamondPack[]> {
  const { data } = await apiClient.get<Paginated<DiamondPack>>("/payments/packs/", { params: { page_size: 20 } });
  return data.results;
}

export async function createStripeCheckout(packId: string): Promise<string> {
  const { data } = await apiClient.post<{ checkout_url: string }>("/payments/checkout/stripe/", { pack_id: packId });
  return data.checkout_url;
}
