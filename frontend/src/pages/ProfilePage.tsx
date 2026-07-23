import { useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { useCountUp } from "@/hooks/useCountUp";
import { LEAGUE_COLORS, LEAGUE_LABELS } from "@/lib/leagues";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";

export default function ProfilePage() {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const { profile, isLoading, refresh } = useProfileStore();

  useEffect(() => {
    void refresh();
  }, [refresh]);

  function handleLogout() {
    logout();
    navigate("/connexion", { replace: true });
  }

  if (isLoading && !profile) return <Loader label="Chargement du profil..." />;
  if (!profile) return <ErrorMessage message="Impossible de charger le profil." onRetry={() => void refresh()} />;

  const xpIntoLevel = profile.xp % 100;

  return (
    <section className="min-h-screen p-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-game flex flex-col items-center text-center"
      >
        <div className="flex h-24 w-24 items-center justify-center overflow-hidden rounded-full border-4 border-haiti-blueLight bg-haiti-blue/10 text-4xl shadow-card">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt="Avatar" className="h-full w-full object-cover" />
          ) : (
            "👤"
          )}
        </div>
        <h1 className="mt-3 text-xl font-display text-haiti-blue">{profile.user.username}</h1>
        <span
          className={`mt-2 rounded-pill px-3 py-1 text-xs font-display text-white ${LEAGUE_COLORS[profile.league]}`}
        >
          Ligue {LEAGUE_LABELS[profile.league]}
        </span>

        <div className="mt-4 w-full">
          <div className="flex justify-between text-sm font-display text-slate-500">
            <span>Niveau {profile.level}</span>
            <span>{xpIntoLevel}/100 XP</span>
          </div>
          <div className="mt-1 h-3 overflow-hidden rounded-pill border-2 border-haiti-blue/10 bg-white">
            <motion.div
              className="h-full rounded-pill bg-haiti-green"
              animate={{ width: `${xpIntoLevel}%` }}
              transition={{ type: "spring", stiffness: 200, damping: 25 }}
            />
          </div>
        </div>
      </motion.div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <StatCard label="Pieces" value={profile.coins} icon="🪙" />
        <StatCard label="Diamants" value={profile.diamonds} icon="💎" />
        <StatCard label="Trophees" value={profile.trophies} icon="🏆" />
        <StatCard label="Serie de victoires" value={profile.win_streak} icon="🔥" />
      </div>

      <div className="card-game mt-4 text-sm text-slate-600">
        <p>
          <strong>Departement :</strong> {profile.department_detail?.name ?? "Non renseigne"}
        </p>
        <p>
          <strong>Meilleure serie :</strong> {profile.best_win_streak} victoires
        </p>
      </div>

      <button type="button" onClick={handleLogout} className="btn-game-secondary mt-6 w-full">
        Se deconnecter
      </button>
    </section>
  );
}

function StatCard({ label, value, icon }: { label: string; value: number; icon: string }) {
  const animatedValue = useCountUp(value);
  return (
    <div className="card-game flex flex-col items-center py-4">
      <span className="text-2xl animate-coin-bounce">{icon}</span>
      <span className="mt-1 font-display text-lg text-haiti-blue">{animatedValue}</span>
      <span className="text-xs text-slate-500">{label}</span>
    </div>
  );
}
