import type { HeroLook } from "@/components/ui/HeroPortrait";

/**
 * Allure cartoon de chaque heros (teint, coiffe/couvre-chef, accessoire),
 * indexee par `Hero.slug`. Definie cote front plutot qu'illustree par un
 * vrai fichier image : voir HeroPortrait.tsx pour le rendu SVG.
 */
export const HERO_PORTRAITS: Record<string, HeroLook> = {
  // --- Heros de chapitre ---
  "toussaint-louverture": { skin: "#8D5524", hair: "bicorne", accent: "#FFD447", facialHair: "mustache" },
  "jean-jacques-dessalines": { skin: "#6B4226", hair: "bicorne", accent: "#D21034", facialHair: "mustache" },
  "henri-christophe": { skin: "#7A4B2A", hair: "crown", accent: "#FFD447" },
  "alexandre-petion": { skin: "#C68642", hair: "topHat", accent: "#0057B8" },
  "catherine-flon": { skin: "#8D5524", hair: "headwrap", accent: "#0057B8" },
  "capois-la-mort": { skin: "#5C3A21", hair: "bicorne", accent: "#FFD447", facialHair: "mustache" },
  "charlemagne-peralte": { skin: "#6B4226", hair: "bandana", accent: "#D21034" },
  anacaona: { skin: "#D2986B", hair: "crown", accent: "#4CAF50" },
  "sanite-belair": { skin: "#5C3A21", hair: "headwrap", accent: "#0057B8" },
  "marie-jeanne-lamartiniere": { skin: "#7A4B2A", hair: "headwrap", accent: "#D21034" },

  // --- Heros bonus (premiere vague) ---
  "dutty-boukman": { skin: "#4A2E1A", hair: "strawHat", accent: "#8B5E34", facialHair: "beard" },
  "cecile-fatiman": { skin: "#6B4226", hair: "headwrap", accent: "#8E44AD" },
  "vincent-oge": { skin: "#C68642", hair: "topHat", accent: "#0057B8" },
  "jean-baptiste-chavannes": { skin: "#8D5524", hair: "bandana", accent: "#4CAF50" },
  "nicolas-geffrard": { skin: "#A9673F", hair: "afro", hairColor: "#241608", accent: "#FFD447" },
  "justin-lherisson": { skin: "#C68642", hair: "beret", accent: "#0057B8" },
  "oswald-durand": { skin: "#8D5524", hair: "beret", accent: "#D21034" },
  "jean-price-mars": { skin: "#6B4226", hair: "topHat", accent: "#4CAF50" },
  "nemours-jean-baptiste": { skin: "#5C3A21", hair: "afro", hairColor: "#1a1a1a", accent: "#FFD447" },
  "jovenel-moise": { skin: "#6B4226", hair: "shortHair", accent: "#0057B8" },

  // --- Heros bonus (deuxieme vague) ---
  "marie-claire-heureuse-bonheur": { skin: "#C68642", hair: "crown", accent: "#FFD447" },
  "stenio-vincent": { skin: "#8D5524", hair: "topHat", accent: "#4CAF50" },
  "jacques-roumain": { skin: "#A9673F", hair: "beret", accent: "#D21034" },
  "faustin-soulouque": { skin: "#5C3A21", hair: "crown", accent: "#D21034" },
  "fabre-geffrard": { skin: "#7A4B2A", hair: "topHat", accent: "#0057B8" },
  "marie-vieux-chauvet": { skin: "#C68642", hair: "headwrap", accent: "#8E44AD" },
  "antenor-firmin": { skin: "#6B4226", hair: "topHat", accent: "#4CAF50", facialHair: "mustache" },
  "benoit-batraville": { skin: "#5C3A21", hair: "bandana", accent: "#D21034" },
  "dumarsais-estime": { skin: "#8D5524", hair: "topHat", accent: "#FFD447" },
  franketienne: { skin: "#6B4226", hair: "beret", accent: "#8E44AD", facialHair: "beard" },
};

export const DEFAULT_HERO_LOOK: HeroLook = { skin: "#8D5524", hair: "shortHair", accent: "#0057B8" };

export function getHeroLook(slug: string): HeroLook {
  return HERO_PORTRAITS[slug] ?? DEFAULT_HERO_LOOK;
}
