import { describe, expect, it } from "vitest";

import { LEAGUE_COLORS, LEAGUE_LABELS } from "./leagues";
import type { League } from "@/types/api";

const ALL_LEAGUES: League[] = ["bronze", "silver", "gold", "platinum", "diamond", "master", "champion"];

describe("leagues", () => {
  it("has a label for every league", () => {
    for (const league of ALL_LEAGUES) {
      expect(LEAGUE_LABELS[league]).toBeTruthy();
    }
  });

  it("has a color class for every league", () => {
    for (const league of ALL_LEAGUES) {
      expect(LEAGUE_COLORS[league]).toMatch(/^bg-league-/);
    }
  });

  it("labels champion as 'Champion National'", () => {
    expect(LEAGUE_LABELS.champion).toBe("Champion National");
  });
});
