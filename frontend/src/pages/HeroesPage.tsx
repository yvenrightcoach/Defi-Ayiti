import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import ErrorMessage from "@/components/ui/ErrorMessage";
import HeroPortrait from "@/components/ui/HeroPortrait";
import Loader from "@/components/ui/Loader";
import { getHeroLook } from "@/data/heroPortraits";
import { getErrorMessage } from "@/lib/errors";
import { setAvatarHero } from "@/services/endpoints/auth";
import { listHeroes } from "@/services/endpoints/heroes";
import { useProfileStore } from "@/store/profileStore";
import type { Hero } from "@/types/api";

const RARITY_STYLES: Record<Hero["rarity"], { label: string; ring: string; badge: string; glow: string }> = {
  common: { label: "Commun", ring: "border-slate-200", badge: "bg-slate-100 text-slate-500", glow: "" },
  rare: { label: "Rare", ring: "border-haiti-blue/40", badge: "bg-haiti-blueLight text-haiti-blue", glow: "" },
  epic: { label: "Epique", ring: "border-purple-400", badge: "bg-purple-100 text-purple-600", glow: "shadow-[0_0_16px_theme(colors.purple.300)]" },
  legendary: { label: "Legendaire", ring: "border-haiti-yellow", badge: "bg-haiti-yellow/30 text-haiti-yellowDark", glow: "shadow-[0_0_20px_theme(colors.haiti.yellow)]" },
};

function requirementText(hero: Hero): string {
  if (hero.department) {
    return hero.department_name
      ? `Termine le chapitre du departement ${hero.department_name}`
      : "Termine le chapitre d'aventure lie a ce heros";
  }
  return `Progresse jusqu'au niveau ${hero.unlock_level} pour avoir une chance de le debloquer`;
}

export default function HeroesPage() {
  const { profile, refresh: refreshProfile } = useProfileStore();
  const [heroes, setHeroes] = useState<Hero[]>([]);
  const [selected, setSelected] = useState<Hero | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSettingAvatar, setIsSettingAvatar] = useState(false);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setHeroes(await listHeroes());
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de charger la collection de heros."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void load();
    if (!profile) void refreshProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleUseAsAvatar(hero: Hero) {
    setIsSettingAvatar(true);
    try {
      await setAvatarHero(hero.id);
      await refreshProfile();
    } catch {
      // Silencieux : l'avatar reste inchange si la requete echoue, pas bloquant pour la collection.
    } finally {
      setIsSettingAvatar(false);
    }
  }

  if (isLoading) return <Loader label="Chargement des heros..." />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  const unlockedCount = heroes.filter((h) => h.is_unlocked).length;
  const progressPercent = heroes.length ? Math.round((unlockedCount / heroes.length) * 100) : 0;

  const chapterHeroes = heroes.filter((h) => h.department);
  const bonusHeroes = [...heroes.filter((h) => !h.department)].sort(
    (a, b) => a.unlock_level - b.unlock_level || a.order - b.order,
  );

  return (
    <section className="min-h-screen p-4">
      <div className="mb-1 flex items-center gap-3">
        <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-haiti-yellow text-2xl shadow-card">
          🎖️
        </span>
        <h1 className="font-display text-2xl text-haiti-blue">Collection de heros</h1>
      </div>
      <p className="mb-2 text-sm text-slate-500">
        {unlockedCount}/{heroes.length} heros debloques {profile ? `· Niveau ${profile.level}` : ""}
      </p>
      <div className="mb-5 h-3 overflow-hidden rounded-pill border-2 border-haiti-blue/10 bg-white">
        <motion.div
          className="h-full rounded-pill bg-haiti-yellow"
          animate={{ width: `${progressPercent}%` }}
          transition={{ type: "spring", stiffness: 200, damping: 25 }}
        />
      </div>

      <HeroSection title="Heros de chapitre" subtitle="Garantis en terminant le chapitre boss de chaque departement" heroes={chapterHeroes} onSelect={setSelected} />
      <HeroSection
        title="Heros bonus"
        subtitle="Echelle de progression : plus ton niveau de joueur augmente, plus les raretes rares deviennent accessibles"
        heroes={bonusHeroes}
        onSelect={setSelected}
        className="mt-6"
      />

      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6"
            onClick={() => setSelected(null)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="card-game max-w-sm text-center"
            >
              <HeroPortrait look={getHeroLook(selected.slug)} rarity={selected.rarity} className="mx-auto h-28 w-28" />
              <h2 className="mt-2 text-xl font-display text-haiti-blue">{selected.name}</h2>
              <span className={`mt-1 inline-block rounded-pill px-2 py-0.5 text-xs font-display ${RARITY_STYLES[selected.rarity].badge}`}>
                {RARITY_STYLES[selected.rarity].label}
              </span>
              {selected.is_unlocked ? (
                <>
                  <p className="mt-3 text-sm text-slate-600">{selected.biography}</p>
                  {selected.quote && <p className="mt-2 italic text-slate-500">"{selected.quote}"</p>}
                  <button
                    type="button"
                    onClick={() => void handleUseAsAvatar(selected)}
                    disabled={isSettingAvatar || profile?.avatar_hero?.id === selected.id}
                    className="btn-game-primary mt-4 w-full disabled:opacity-60"
                  >
                    {profile?.avatar_hero?.id === selected.id
                      ? "Deja ta photo de profil"
                      : isSettingAvatar
                        ? "..."
                        : "Utiliser comme photo de profil"}
                  </button>
                </>
              ) : (
                <p className="mt-3 text-sm text-slate-500">🔒 {requirementText(selected)}</p>
              )}
              <button type="button" onClick={() => setSelected(null)} className="btn-game-secondary mt-3 w-full">
                Fermer
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}

function HeroSection({
  title,
  subtitle,
  heroes,
  onSelect,
  className = "",
}: {
  title: string;
  subtitle: string;
  heroes: Hero[];
  onSelect: (hero: Hero) => void;
  className?: string;
}) {
  if (heroes.length === 0) return null;
  return (
    <div className={className}>
      <h2 className="font-display text-haiti-blue">{title}</h2>
      <p className="mb-3 text-xs text-slate-400">{subtitle}</p>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {heroes.map((hero, index) => {
          const rarity = RARITY_STYLES[hero.rarity];
          return (
            <motion.button
              key={hero.id}
              type="button"
              initial={{ opacity: 0, y: 10, scale: 0.85 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: index * 0.04, type: "spring", stiffness: 300, damping: 20 }}
              onClick={() => onSelect(hero)}
              className={`card-game flex flex-col items-center gap-1 border-2 py-4 text-center transition-all duration-150 ${
                hero.is_unlocked
                  ? `${rarity.ring} ${rarity.glow} hover:-translate-y-1 hover:shadow-card-hover active:translate-y-0`
                  : "border-slate-100 hover:-translate-y-0.5"
              }`}
            >
              <HeroPortrait
                look={getHeroLook(hero.slug)}
                rarity={hero.rarity}
                locked={!hero.is_unlocked}
                className="h-16 w-16"
              />
              <span className="font-display text-sm text-haiti-blue">{hero.name}</span>
              <span className={`rounded-pill px-2 py-0.5 text-xs font-display ${rarity.badge}`}>{rarity.label}</span>
              {!hero.is_unlocked && !hero.department && (
                <span className="text-[10px] text-slate-400">Niveau {hero.unlock_level}+</span>
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
