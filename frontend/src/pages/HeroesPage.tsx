import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { getErrorMessage } from "@/lib/errors";
import { listHeroes } from "@/services/endpoints/heroes";
import type { Hero } from "@/types/api";

export default function HeroesPage() {
  const [heroes, setHeroes] = useState<Hero[]>([]);
  const [selected, setSelected] = useState<Hero | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
  }, []);

  if (isLoading) return <Loader label="Chargement des heros..." />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  const unlockedCount = heroes.filter((h) => h.is_unlocked).length;

  return (
    <section className="min-h-screen p-4">
      <h1 className="text-2xl font-display text-haiti-blue">Collection de heros</h1>
      <p className="mb-4 text-sm text-slate-500">
        {unlockedCount}/{heroes.length} heros debloques
      </p>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {heroes.map((hero, index) => (
          <motion.button
            key={hero.id}
            type="button"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.04 }}
            onClick={() => hero.is_unlocked && setSelected(hero)}
            className={`card-game flex flex-col items-center gap-1 py-4 text-center ${
              hero.is_unlocked ? "active:scale-95" : "opacity-50 grayscale"
            }`}
          >
            <span className="text-4xl">{hero.is_unlocked ? "🎖️" : "🔒"}</span>
            <span className="font-display text-sm text-haiti-blue">{hero.name}</span>
            <span className="text-xs capitalize text-slate-400">{hero.rarity}</span>
          </motion.button>
        ))}
      </div>

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
              <span className="text-5xl">🎖️</span>
              <h2 className="mt-2 text-xl font-display text-haiti-blue">{selected.name}</h2>
              <p className="mt-2 text-sm text-slate-600">{selected.biography}</p>
              {selected.quote && <p className="mt-2 italic text-slate-500">"{selected.quote}"</p>}
              <button type="button" onClick={() => setSelected(null)} className="btn-game-secondary mt-4 w-full">
                Fermer
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
