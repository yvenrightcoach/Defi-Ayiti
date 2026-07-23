import { useEffect } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import Loader from "@/components/ui/Loader";
import { useCountUp } from "@/hooks/useCountUp";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";

const QUICK_LINKS = [
  { to: "/aventure", label: "Mode Aventure", icon: "🗺️", color: "bg-haiti-blue" },
  { to: "/quiz", label: "Quiz rapide", icon: "❓", color: "bg-haiti-green" },
  { to: "/battle", label: "Battle", icon: "⚔️", color: "bg-haiti-red" },
  { to: "/heros", label: "Mes heros", icon: "🎖️", color: "bg-haiti-yellow text-haiti-blue" },
  { to: "/amis", label: "Amis", icon: "🤝", color: "bg-haiti-blue" },
  { to: "/classements", label: "Classements", icon: "🏆", color: "bg-haiti-green" },
];

export default function HomePage() {
  const accessToken = useAuthStore((state) => state.accessToken);
  const { profile, isLoading, refresh } = useProfileStore();

  useEffect(() => {
    if (accessToken) void refresh();
  }, [accessToken, refresh]);

  const coins = useCountUp(profile?.coins ?? 0);
  const diamonds = useCountUp(profile?.diamonds ?? 0);
  const trophies = useCountUp(profile?.trophies ?? 0);

  if (isLoading && !profile) {
    return <Loader label="Chargement de ton profil..." />;
  }

  const xpIntoLevel = (profile?.xp ?? 0) % 100;

  return (
    <div className="min-h-screen bg-haiti-blue/5 p-4">
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-game mb-4 bg-haiti-blue text-white"
      >
        <p className="text-sm text-haiti-yellow">Byenveni,</p>
        <h1 className="text-2xl font-display">{profile?.user.username ?? "Joueur"}</h1>
        <div className="mt-3 flex items-center justify-between text-sm">
          <span>Niveau {profile?.level ?? 1}</span>
          <span>{xpIntoLevel}/100 XP</span>
        </div>
        <div className="mt-1 h-2 overflow-hidden rounded-pill bg-white/20">
          <div className="h-full rounded-pill bg-haiti-yellow" style={{ width: `${xpIntoLevel}%` }} />
        </div>
        <div className="mt-4 flex justify-between text-center text-sm">
          <div>
            <p className="font-display text-lg">{coins}</p>
            <p className="text-white/70">Pieces</p>
          </div>
          <div>
            <p className="font-display text-lg">{diamonds}</p>
            <p className="text-white/70">Diamants</p>
          </div>
          <div>
            <p className="font-display text-lg">{trophies}</p>
            <p className="text-white/70">Trophees</p>
          </div>
        </div>
      </motion.section>

      <div className="grid grid-cols-2 gap-3">
        {QUICK_LINKS.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`${link.color} flex flex-col items-center justify-center gap-1 rounded-card p-6 text-white shadow-card transition-transform active:scale-95`}
          >
            <span className="text-3xl">{link.icon}</span>
            <span className="font-display">{link.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
