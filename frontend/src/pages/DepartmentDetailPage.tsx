import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate, useParams } from "react-router-dom";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { getErrorMessage } from "@/lib/errors";
import { getDepartment } from "@/services/endpoints/geography";
import { listProgress } from "@/services/endpoints/progress";
import type { DepartmentDetail, Level, PlayerProgress } from "@/types/api";

export default function DepartmentDetailPage() {
  const { departmentId } = useParams<{ departmentId: string }>();
  const navigate = useNavigate();
  const [department, setDepartment] = useState<DepartmentDetail | null>(null);
  const [progress, setProgress] = useState<PlayerProgress | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  if (isLoading) return <Loader label="Chargement du departement..." />;
  if (error || !department) return <ErrorMessage message={error ?? "Departement introuvable."} onRetry={load} />;

  const currentOrder = progress?.current_level_detail?.order ?? 0;
  const levels = [...department.levels].sort((a, b) => a.order - b.order);

  function isUnlocked(level: Level) {
    return level.order <= currentOrder + 1;
  }

  return (
    <section className="min-h-screen bg-haiti-blue/5 p-4">
      <Link to="/aventure" className="mb-2 inline-block text-sm text-haiti-blue">
        ← Retour a la carte
      </Link>
      <h1 className="text-2xl font-display text-haiti-blue">{department.name}</h1>
      <p className="mb-4 text-sm text-slate-500">{department.description}</p>

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
              onClick={() => navigate(`/quiz/level/${level.id}`)}
              className={`card-game flex w-full items-center justify-between text-left transition-transform ${
                unlocked ? "active:scale-95" : "opacity-50"
              }`}
            >
              <div>
                <p className="font-display text-haiti-blue">
                  {level.is_boss_level ? "👑 " : ""}
                  Chapitre {level.order} : {level.name}
                </p>
                <p className="text-xs text-slate-400">
                  {level.question_count} questions · +{level.xp_reward} XP · +{level.coin_reward} pieces
                </p>
              </div>
              <span className="text-2xl">{unlocked ? "▶️" : "🔒"}</span>
            </motion.button>
          );
        })}
      </div>
    </section>
  );
}
