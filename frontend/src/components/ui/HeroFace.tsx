import { getHeroLook } from "@/data/heroPortraits";
import type { HeroRarity } from "@/types/api";

import HeroPortrait from "./HeroPortrait";

interface HeroFaceProps {
  hero: { image: string; slug: string; rarity: HeroRarity };
  locked?: boolean;
  className?: string;
}

/**
 * Visage d'un heros : vraie illustration/photo historique quand on en a une
 * fiable (voir `image`, peuple par seed_content.py), sinon portrait cartoon
 * de secours (HeroPortrait) -- une majorite des heros d'avant 1830 n'ont
 * jamais ete photographies ni peints de leur vivant.
 */
export default function HeroFace({ hero, locked = false, className = "" }: HeroFaceProps) {
  if (!hero.image) {
    return <HeroPortrait look={getHeroLook(hero.slug)} rarity={hero.rarity} locked={locked} className={className} />;
  }
  return (
    <div className={`relative overflow-hidden rounded-full bg-slate-100 ${className}`}>
      <img
        src={hero.image}
        alt=""
        className="h-full w-full object-cover"
        style={locked ? { filter: "grayscale(1)", opacity: 0.55 } : undefined}
      />
      {locked && (
        <span className="absolute inset-0 flex items-end justify-end p-1">
          <span className="flex h-1/3 w-1/3 items-center justify-center rounded-full bg-black/70 text-[10px]">🔒</span>
        </span>
      )}
    </div>
  );
}
