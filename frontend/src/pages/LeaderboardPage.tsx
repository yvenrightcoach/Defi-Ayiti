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
      <h1 className="mb-4 text-2xl font-display text-haiti-blue">Classements</h1>

      <div className="mb-3 flex gap-2 overflow-x-auto">
        {SCOPES.map((s) => (
          <button
            key={s.value}
            type="button"
            onClick={() => setScope(s.value)}
            className={`whitespace-nowrap rounded-pill px-4 py-1.5 text-sm font-display ${
              scope === s.value ? "bg-haiti-blue text-white" : "bg-white text-haiti-blue"
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
            className={`whitespace-nowrap rounded-pill px-4 py-1.5 text-sm ${
              period === p.value ? "bg-haiti-yellow text-haiti-blue" : "bg-white text-slate-500"
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
          {entries.map((entry, index) => (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.02 }}
              className={`card-game flex items-center gap-3 py-3 ${
                entry.profile.id === profile?.id ? "ring-2 ring-haiti-yellow" : ""
              }`}
            >
              <span className="w-8 text-center font-display text-haiti-blue">#{entry.rank}</span>
              <span className="flex-1 truncate">{entry.profile.user.username}</span>
              <span className="font-display text-haiti-blue">{entry.score} pts</span>
            </motion.div>
          ))}
        </div>
      )}
    </section>
  );
}
