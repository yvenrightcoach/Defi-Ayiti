import { useEffect, useState } from "react";
import { motion } from "framer-motion";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { getErrorMessage } from "@/lib/errors";
import { listLeaderboard } from "@/services/endpoints/competition";
import { useProfileStore } from "@/store/profileStore";
import type { LeaderboardEntry, LeaderboardPeriod, LeaderboardScope } from "@/types/api";

const SCOPES: { value: LeaderboardScope; label: string }[] = [
  { value: "national", label: "National" },
  { value: "department", label: "Departement" },
  { value: "friends", label: "Amis" },
];

const PERIODS: { value: LeaderboardPeriod; label: string }[] = [
  { value: "weekly", label: "Semaine" },
  { value: "monthly", label: "Mois" },
  { value: "yearly", label: "Annee" },
];

export default function LeaderboardPage() {
  const { profile, refresh: refreshProfile } = useProfileStore();
  const [scope, setScope] = useState<LeaderboardScope>("national");
  const [period, setPeriod] = useState<LeaderboardPeriod>("weekly");
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setEntries(await listLeaderboard(scope, period, profile?.department ?? undefined));
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de charger le classement."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (!profile) void refreshProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scope, period]);

  return (
    <section className="min-h-screen p-4">
      <div className="mb-4 flex items-center gap-3">
        <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-haiti-green text-2xl shadow-card">
          🏆
        </span>
        <h1 className="font-display text-2xl text-haiti-blue">Classements</h1>
      </div>

      <div className="mb-3 flex gap-2 overflow-x-auto">
        {SCOPES.map((s) => (
          <button
            key={s.value}
            type="button"
            onClick={() => setScope(s.value)}
            className={`whitespace-nowrap rounded-pill border-2 px-4 py-1.5 text-sm font-display transition-all duration-150 ${
              scope === s.value
                ? "border-haiti-blue bg-haiti-blue text-white"
                : "border-slate-100 bg-white text-haiti-blue"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>
      <div className="mb-4 flex gap-2 overflow-x-auto">
        {PERIODS.map((p) => (
          <button
            key={p.value}
            type="button"
            onClick={() => setPeriod(p.value)}
            className={`whitespace-nowrap rounded-pill border-2 px-4 py-1.5 text-sm transition-all duration-150 ${
              period === p.value
                ? "border-haiti-yellow bg-haiti-yellow text-haiti-blue"
                : "border-slate-100 bg-white text-slate-500"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <Loader label="Chargement du classement..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={load} />
      ) : entries.length === 0 ? (
        <p className="text-center text-slate-500">Aucun classement disponible pour le moment.</p>
      ) : (
        <div className="space-y-2">
          {entries.map((entry, index) => {
            const medal = entry.rank === 1 ? "🥇" : entry.rank === 2 ? "🥈" : entry.rank === 3 ? "🥉" : null;
            return (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.02 }}
                className={`card-game flex items-center gap-3 py-3 ${
                  entry.profile.id === profile?.id ? "border-haiti-yellow ring-2 ring-haiti-yellow" : ""
                } ${medal ? "bg-haiti-yellow/10" : ""}`}
              >
                <span
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full font-display ${
                    medal ? "text-2xl" : "bg-haiti-blueLight text-haiti-blue"
                  }`}
                >
                  {medal ?? `#${entry.rank}`}
                </span>
                <span className="flex-1 truncate font-display text-slate-700">{entry.profile.user.username}</span>
                <span className="rounded-pill bg-haiti-blueLight px-2 py-1 font-display text-sm text-haiti-blue">
                  {entry.score} pts
                </span>
              </motion.div>
            );
          })}
        </div>
      )}
    </section>
  );
}
