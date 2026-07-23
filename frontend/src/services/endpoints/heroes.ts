import { apiClient } from "@/services/apiClient";
import type { Hero, HeroCard, Paginated } from "@/types/api";

export async function listHeroes(): Promise<Hero[]> {
  const { data } = await apiClient.get<Paginated<Hero>>("/heroes/heroes/", { params: { page_size: 50 } });
  return data.results;
}

export async function listHeroCards(): Promise<HeroCard[]> {
  const { data } = await apiClient.get<Paginated<HeroCard>>("/heroes/cards/", { params: { page_size: 50 } });
  return data.results;
}
