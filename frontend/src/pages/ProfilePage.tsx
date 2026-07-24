import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate, useSearchParams } from "react-router-dom";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { useCountUp } from "@/hooks/useCountUp";
import { LEAGUE_COLORS, LEAGUE_LABELS } from "@/lib/leagues";
import { createStripeCheckout, listDiamondPacks } from "@/services/endpoints/payments";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { useSoundStore } from "@/store/soundStore";
import type { DiamondPack } from "@/types/api";

function formatUsd(cents: number): string {
  return `${(cents / 100).toFixed(2)} $`;
}

export default function ProfilePage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const logout = useAuthStore((state) => state.logout);
  const { profile, isLoading, refresh } = useProfileStore();
  const soundEnabled = useSoundStore((state) => state.enabled);
  const toggleSound = useSoundStore((state) => state.toggle);

  const [packs, setPacks] = useState<DiamondPack[]>([]);
  const [processingPackId, setProcessingPackId] = useState<string | null>(null);
  const [purchaseError, setPurchaseError] = useState<string | null>(null);
  const [paymentBanner] = useState<string | null>(() => searchParams.get("paiement"));

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    void listDiamondPacks().then(setPacks);
  }, []);

  useEffect(() => {
    if (!paymentBanner) return;
    if (paymentBanner === "succes") void refresh();
    const next = new URLSearchParams(searchParams);
    next.delete("paiement");
    setSearchParams(next, { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleBuyPack(pack: DiamondPack) {
    setPurchaseError(null);
    setProcessingPackId(pack.id);
    try {
      const checkoutUrl = await createStripeCheckout(pack.id);
      window.location.href = checkoutUrl;
    } catch {
      setPurchaseError("Impossible de lancer le paiement pour le moment.");
      setProcessingPackId(null);
    }
  }

  function handleLogout() {
    logout();
    navigate("/connexion", { replace: true });
  }

  if (isLoading && !profile) return <Loader label="Chargement du profil..." />;
  if (!profile) return <ErrorMessage message="Impossible de charger le profil." onRetry={() => void refresh()} />;

  const xpIntoLevel = profile.xp % 100;

  return (
    <section className="min-h-screen p-4">
      {paymentBanner === "succes" && (
        <div className="card-game mb-3 bg-haiti-green/10 text-center font-display text-haiti-green">
          Paiement reussi, tes diamants sont credites !
        </div>
      )}
      {paymentBanner === "annule" && (
        <div className="card-game mb-3 bg-slate-100 text-center font-display text-slate-500">
          Paiement annule.
        </div>
      )}

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

      {packs.length > 0 && (
        <div className="card-game mt-4">
          <p className="mb-2 font-display text-haiti-blue">💎 Acheter des diamants</p>
          {purchaseError && <p className="mb-2 text-sm text-haiti-red">{purchaseError}</p>}
          <div className="space-y-2">
            {packs.map((pack) => (
              <button
                key={pack.id}
                type="button"
                onClick={() => handleBuyPack(pack)}
                disabled={processingPackId !== null}
                className="btn-game-outline flex w-full items-center justify-between disabled:opacity-60"
              >
                <span>
                  💎 {pack.diamonds_amount} diamants
                </span>
                <span>{processingPackId === pack.id ? "..." : formatUsd(pack.price_usd_cents)}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="card-game mt-4 text-sm text-slate-600">
        <p>
          <strong>Departement :</strong> {profile.department_detail?.name ?? "Non renseigne"}
        </p>
        <p>
          <strong>Meilleure serie :</strong> {profile.best_win_streak} victoires
        </p>
      </div>

      <button
        type="button"
        onClick={toggleSound}
        className="card-game mt-4 flex w-full items-center justify-between text-left"
      >
        <span className="font-display text-slate-700">
          {soundEnabled ? "🔊 Sons actives" : "🔇 Sons desactives"}
        </span>
        <span
          className={`flex h-7 w-12 items-center rounded-pill p-1 transition-colors ${
            soundEnabled ? "justify-end bg-haiti-green" : "justify-start bg-slate-300"
          }`}
        >
          <span className="h-5 w-5 rounded-full bg-white shadow" />
        </span>
      </button>

      <button type="button" onClick={handleLogout} className="btn-game-secondary mt-4 w-full">
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
