import type { HeroRarity } from "@/types/api";

export type HeroHairStyle =
  | "bicorne"
  | "headwrap"
  | "crown"
  | "topHat"
  | "beret"
  | "afro"
  | "strawHat"
  | "bandana"
  | "shortHair";

export interface HeroLook {
  skin: string;
  hair: HeroHairStyle;
  /** Couleur des cheveux visibles (afro/courts) et du poil facial. */
  hairColor?: string;
  /** Couleur du couvre-chef / ruban / galon (chapeau, foulard, couronne...). */
  accent: string;
  facialHair?: "mustache" | "beard";
}

const RARITY_BACKDROP: Record<HeroRarity, [string, string]> = {
  common: ["#CBD5E1", "#E2E8F0"],
  rare: ["#BBD9FF", "#EAF3FF"],
  epic: ["#D8B4FE", "#F3E8FF"],
  legendary: ["#FFD447", "#FFF3D0"],
};

interface HeroPortraitProps {
  look: HeroLook;
  rarity: HeroRarity;
  className?: string;
  locked?: boolean;
}

/**
 * Portrait cartoon genere en SVG (pas d'asset image a charger) : chaque
 * heros a une allure distincte (teint, coiffe/couvre-chef, accessoire)
 * definie dans heroPortraits.ts, plutot qu'une vraie photo -- coherent avec
 * le style illustratif deja utilise pour la mascotte Ti Kok.
 */
export default function HeroPortrait({ look, rarity, className = "", locked = false }: HeroPortraitProps) {
  const [bgEdge, bgCenter] = RARITY_BACKDROP[rarity];
  const hairColor = look.hairColor ?? "#2b1b12";
  const gradientId = `hero-bg-${rarity}`;

  return (
    <svg
      viewBox="0 0 120 130"
      className={className}
      role="img"
      aria-hidden="true"
      style={locked ? { filter: "grayscale(1)", opacity: 0.55 } : undefined}
    >
      <defs>
        <radialGradient id={gradientId} cx="50%" cy="38%" r="70%">
          <stop offset="0%" stopColor={bgCenter} />
          <stop offset="100%" stopColor={bgEdge} />
        </radialGradient>
      </defs>

      <circle cx="60" cy="62" r="58" fill={`url(#${gradientId})`} />

      {/* Epaules / col */}
      <path d="M14 130 C 14 100, 36 88, 60 88 C 84 88, 106 100, 106 130 Z" fill="#0057B8" />
      <path d="M46 94 L60 108 L74 94 L69 88 L60 95 L51 88 Z" fill="#FFFFFF" opacity="0.85" />

      {/* Oreilles */}
      <circle cx="29" cy="65" r="5" fill={look.skin} />
      <circle cx="91" cy="65" r="5" fill={look.skin} />

      {/* Tete */}
      <ellipse cx="60" cy="62" rx="30" ry="32" fill={look.skin} />

      {renderHeadwear(look.hair, look.accent, hairColor)}

      {/* Sourcils */}
      <path d="M42 55 Q 48 51 54 55" stroke={hairColor} strokeWidth="2.5" fill="none" strokeLinecap="round" />
      <path d="M66 55 Q 72 51 78 55" stroke={hairColor} strokeWidth="2.5" fill="none" strokeLinecap="round" />

      {/* Yeux */}
      <circle cx="48" cy="63" r="4" fill="#1a1a1a" />
      <circle cx="49.4" cy="61.5" r="1.3" fill="#fff" />
      <circle cx="72" cy="63" r="4" fill="#1a1a1a" />
      <circle cx="73.4" cy="61.5" r="1.3" fill="#fff" />

      {/* Joues */}
      <circle cx="41" cy="73" r="5" fill="#D21034" opacity="0.15" />
      <circle cx="79" cy="73" r="5" fill="#D21034" opacity="0.15" />

      {/* Bouche */}
      <path d="M50 81 Q 60 88 70 81" stroke="#5c2e1a" strokeWidth="2.5" fill="none" strokeLinecap="round" />

      {look.facialHair === "mustache" && (
        <path d="M45 77 Q 60 83 75 77 Q 60 73 45 77 Z" fill={hairColor} />
      )}
      {look.facialHair === "beard" && (
        <path
          d="M39 75 C 41 94, 50 102, 60 102 C 70 102, 79 94, 81 75 C 74 88, 66 92, 60 92 C 54 92, 46 88, 39 75 Z"
          fill={hairColor}
          opacity="0.92"
        />
      )}

      {locked && (
        <g>
          <circle cx="94" cy="98" r="16" fill="#1a1a1a" opacity="0.75" />
          <rect x="88" y="94" width="12" height="10" rx="2" fill="#FFD447" />
          <path d="M90 94 v-3 a4 4 0 0 1 8 0 v3" stroke="#FFD447" strokeWidth="2.5" fill="none" />
        </g>
      )}
    </svg>
  );
}

function renderHeadwear(hair: HeroHairStyle, accent: string, hairColor: string) {
  switch (hair) {
    case "bicorne":
      return (
        <g>
          <path
            d="M18 46 C 28 20, 92 20, 102 46 C 86 36, 70 44, 60 40 C 50 44, 34 36, 18 46 Z"
            fill="#101820"
          />
          <circle cx="60" cy="36" r="3" fill={accent} />
        </g>
      );
    case "headwrap":
      return (
        <g>
          <path
            d="M25 52 C 22 26, 98 26, 95 52 C 88 39, 76 32, 60 32 C 44 32, 32 39, 25 52 Z"
            fill={accent}
          />
          <path d="M60 32 C 67 28, 77 29, 81 35" stroke="#fff" strokeWidth="2" fill="none" opacity="0.55" />
          <path d="M87 41 C 98 43, 101 54, 92 60 C 95 50, 91 44, 83 41 Z" fill={accent} />
        </g>
      );
    case "crown":
      return (
        <g>
          <path d="M29 47 L33 25 L46 41 L60 20 L74 41 L87 25 L91 47 Z" fill={accent} />
          <circle cx="60" cy="22" r="3" fill="#fff" opacity="0.85" />
        </g>
      );
    case "topHat":
      return (
        <g>
          <rect x="41" y="8" width="38" height="27" rx="3" fill="#101820" />
          <rect x="32" y="33" width="56" height="8" rx="3" fill="#101820" />
          <rect x="41" y="26" width="38" height="6" fill={accent} />
        </g>
      );
    case "beret":
      return (
        <g>
          <path d="M27 45 C 20 19, 100 19, 93 45 C 80 32, 40 32, 27 45 Z" fill={accent} />
          <circle cx="61" cy="19" r="3" fill={accent} />
        </g>
      );
    case "strawHat":
      return (
        <g>
          <ellipse cx="60" cy="39" rx="44" ry="9" fill="#D8B36A" />
          <path d="M35 39 C 35 20, 85 20, 85 39 C 74 31, 46 31, 35 39 Z" fill="#E8C989" />
          <rect x="35" y="37" width="50" height="5" fill={accent} />
        </g>
      );
    case "bandana":
      return (
        <g>
          <path d="M27 49 C 25 30, 95 30, 93 49 C 82 39, 38 39, 27 49 Z" fill={accent} />
          <path d="M89 45 L101 53 L91 57 Z" fill={accent} />
        </g>
      );
    case "afro":
      return <circle cx="60" cy="47" r="35" fill={hairColor} />;
    case "shortHair":
      return (
        <path
          d="M27 51 C 23 23, 97 23, 93 51 C 93 40, 84 34, 60 34 C 36 34, 27 40, 27 51 Z"
          fill={hairColor}
        />
      );
    default:
      return null;
  }
}
