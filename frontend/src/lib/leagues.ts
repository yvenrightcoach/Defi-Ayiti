import type { League } from "@/types/api";

export const LEAGUE_LABELS: Record<League, string> = {
  bronze: "Bronze",
  silver: "Argent",
  gold: "Or",
  platinum: "Platine",
  diamond: "Diamant",
  master: "Maitre",
  champion: "Champion National",
};

export const LEAGUE_COLORS: Record<League, string> = {
  bronze: "bg-league-bronze",
  silver: "bg-league-silver",
  gold: "bg-league-gold",
  platinum: "bg-league-platinum",
  diamond: "bg-league-diamond",
  master: "bg-league-master",
  champion: "bg-league-champion",
};
