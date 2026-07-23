import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { getErrorMessage } from "@/lib/errors";
import { listDepartments } from "@/services/endpoints/geography";
import { listProgress } from "@/services/endpoints/progress";
import type { Department, PlayerProgress } from "@/types/api";

export default function AdventureMapPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [progress, setProgress] = useState<PlayerProgress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [depts, progressEntries] = await Promise.all([listDepartments(), listProgress()]);
      setDepartments(depts);
      setProgress(progressEntries);
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de charger la carte d'Haiti."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  if (isLoading) return <Loader label="Chargement de la carte d'Haiti..." />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  return (
    <section className="min-h-screen p-4">
      <h1 className="mb-1 text-2xl font-display text-haiti-blue">Carte d'Haiti</h1>
      <p className="mb-4 text-sm text-slate-500">Choisis un departement pour commencer ton aventure.</p>

      <div className="grid grid-cols-2 gap-3">
        {departments.map((dept, index) => {
          const deptProgress = progress.find((p) => p.department === dept.id);
          return (
            <motion.div
              key={dept.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.03 }}
            >
              <Link
                to={`/aventure/${dept.id}`}
                className="card-game flex flex-col items-center gap-1 py-5 text-center transition-transform active:scale-95"
              >
                <span className="text-3xl">🏝️</span>
                <span className="font-display text-haiti-blue">{dept.name}</span>
                <span className="text-xs text-slate-400">{dept.capital}</span>
                {deptProgress && (
                  <span className="mt-1 text-xs text-haiti-green">
                    {"⭐".repeat(Math.min(deptProgress.stars, 5)) || "Commence"}
                    {deptProgress.is_completed ? " · Termine" : ""}
                  </span>
                )}
              </Link>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
