import { useEffect, useState } from "react";
import { isAxiosError } from "axios";
import { motion } from "framer-motion";
import { Link, useNavigate, useParams } from "react-router-dom";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { getErrorMessage } from "@/lib/errors";
import { convertDiamondsToCoins } from "@/services/endpoints/auth";
import { getDepartment } from "@/services/endpoints/geography";
import { listProgress, stakeLevel } from "@/services/endpoints/progress";
import { useProfileStore } from "@/store/profileStore";
import type { DepartmentDetail, Level, PlayerProgress } from "@/types/api";

const DIAMOND_TO_COIN_RATE = 10;

export default function DepartmentDetailPage() {
  const { departmentId } = useParams<{ departmentId: string }>();
  const navigate = useNavigate();
  const profile = useProfileStore((state) => state.profile);
  const refreshProfile = useProfileStore((state) => state.refresh);
  const [department, setDepartment] = useState<DepartmentDetail | null>(null);
  const [progress, setProgress] = useState<PlayerProgress | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [stakeTarget, setStakeTarget] = useState<Level | null>(null);
  const [stakeError, setStakeError] = useState<string | null>(null);
  const [missingCoins, setMissingCoins] = useState<number | null>(null);
  const [isStaking, setIsStaking] = useState(false);

  async function load() {
    if (!departmentId) return;
    setIsLoading(true);
    setError(null);
    try {
      const [dept, progressEntries] = await Promise.all([getDepartment(departmentId), listProgress()]);
      setDepartment(dept);
      setProgress(progressEntries.find((p) => p.department === departmentId) ?? null);
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de charger ce departement."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [departmentId]);

  useEffect(() => {
    if (!profile) void refreshProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isLoading) return <Loader label="Chargement du departement..." />;
  if (error || !department) return <ErrorMessage message={error ?? "Departement introuvable."} onRetry={load} />;

  const currentOrder = progress?.current_level_detail?.order ?? 0;
  const levels = [...department.levels].sort((a, b) => a.order - b.order);

  function isUnlocked(level: Level) {
    return level.order <= currentOrder + 1;
  }

  function openStakeModal(level: Level) {
    setStakeError(null);
    setMissingCoins(null);
    setStakeTarget(level);
  }

  function closeStakeModal() {
    if (isStaking) return;
    setStakeTarget(null);
    setStakeError(null);
    setMissingCoins(null);
  }

  async function confirmStake() {
    if (!stakeTarget) return;
    setIsStaking(true);
    setStakeError(null);
    try {
      await stakeLevel(stakeTarget.id);
      await refreshProfile();
      navigate(`/quiz/level/${stakeTarget.id}`);
    } catch (err) {
      if (isAxiosError(err) && err.response?.status === 402) {
        const coins = (err.response.data as { coins?: number }).coins ?? profile?.coins ?? 0;
        setMissingCoins(Math.max(stakeTarget.stake_cost - coins, 0));
        setStakeError("Pas assez de pieces pour miser sur ce chapitre.");
      } else {
        setStakeError(getErrorMessage(err, "Impossible de miser sur ce chapitre."));
      }
    } finally {
      setIsStaking(false);
    }
  }

  async function convertAndRetry() {
    if (!missingCoins) return;
    setIsStaking(true);
    setStakeError(null);
    try {
      const diamondsNeeded = Math.ceil(missingCoins / DIAMOND_TO_COIN_RATE);
      await convertDiamondsToCoins(diamondsNeeded);
      setMissingCoins(null);
      await confirmStake();
    } catch (err) {
      setStakeError(getErrorMessage(err, "Pas assez de diamants pour convertir."));
      setIsStaking(false);
    }
  }

  return (
    <section className="min-h-screen p-4">
      <Link
        to="/aventure"
        className="mb-3 inline-flex items-center gap-1 rounded-pill bg-white px-3 py-1.5 text-sm font-display text-haiti-blue shadow-card"
      >
        ← Retour a la carte
      </Link>

      <div className="mb-4 flex items-center gap-3">
        <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-haiti-blue text-2xl shadow-card">
          🏝️
        </span>
        <div>
          <h1 className="font-display text-2xl text-haiti-blue">{department.name}</h1>
          <p className="text-sm text-slate-500">{department.description}</p>
        </div>
      </div>

      <div className="space-y-3">
        {levels.map((level, index) => {
          const unlocked = isUnlocked(level);
          return (
            <motion.button
              key={level.id}
              type="button"
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              disabled={!unlocked}
              onClick={() => openStakeModal(level)}
              className={`card-game flex w-full items-center gap-3 text-left transition-all duration-150 ${
                unlocked ? "hover:-translate-y-0.5 hover:shadow-card-hover active:translate-y-0" : "opacity-50"
              }`}
            >
              <span
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl font-display text-lg ${
                  unlocked ? "bg-haiti-blueLight text-haiti-blue" : "bg-slate-100 text-slate-400"
                }`}
              >
                {level.is_boss_level ? "👑" : level.order}
              </span>
              <div className="flex-1">
                <p className="font-display text-haiti-blue">
                  {level.is_boss_level ? "👑 " : ""}
                  Chapitre {level.order} : {level.name}
                </p>
                <p className="text-xs text-slate-400">
                  {level.question_count} questions · +{level.xp_reward} XP · +{level.coin_reward} pieces · Mise :{" "}
                  {level.stake_cost} 🪙
                </p>
              </div>
              <span className="text-2xl">{unlocked ? "▶️" : "🔒"}</span>
            </motion.button>
          );
        })}
      </div>

      {stakeTarget && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="card-game w-full max-w-sm"
          >
            <p className="font-display text-lg text-haiti-blue">
              Chapitre {stakeTarget.order} : {stakeTarget.name}
            </p>
            <p className="mt-1 text-sm text-slate-500">
              Mise ta pieces pour tenter ce chapitre. Si tu reussis, tu recuperes ta mise + la recompense. Si tu
              echoues, la mise est perdue.
            </p>

            <div className="card-game mt-3 flex items-center justify-between bg-haiti-blueLight/40">
              <span className="font-display text-slate-600">Mise requise</span>
              <span className="font-display text-haiti-blue">{stakeTarget.stake_cost} 🪙</span>
            </div>
            <div className="mt-1 flex items-center justify-between text-sm text-slate-400">
              <span>Tes pieces</span>
              <span>{profile?.coins ?? "..."} 🪙</span>
            </div>

            {stakeError && (
              <div className="mt-3 rounded-2xl bg-haiti-red/10 p-3 text-sm text-haiti-red">
                <p>{stakeError}</p>
                {missingCoins !== null && (
                  <p className="mt-1 text-xs">
                    Il te manque {missingCoins} pieces (≈ {Math.ceil(missingCoins / DIAMOND_TO_COIN_RATE)} 💎).
                  </p>
                )}
              </div>
            )}

            <div className="mt-4 space-y-2">
              {missingCoins === null ? (
                <button
                  type="button"
                  onClick={confirmStake}
                  disabled={isStaking}
                  className="btn-game-primary w-full disabled:opacity-60"
                >
                  {isStaking ? "..." : `Miser ${stakeTarget.stake_cost} 🪙 et jouer`}
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={convertAndRetry}
                    disabled={isStaking}
                    className="btn-game-primary w-full disabled:opacity-60"
                  >
                    {isStaking ? "..." : `Convertir ${Math.ceil(missingCoins / DIAMOND_TO_COIN_RATE)} 💎 et jouer`}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate("/profil")}
                    className="btn-game-outline w-full"
                  >
                    Acheter des diamants
                  </button>
                </>
              )}
              <button type="button" onClick={closeStakeModal} disabled={isStaking} className="btn-game-secondary w-full">
                Annuler
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </section>
  );
}
