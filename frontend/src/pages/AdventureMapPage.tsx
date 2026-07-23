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
      <div className="mb-4 flex items-center gap-3">
        <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-haiti-blue text-2xl shadow-card">
          🗺️
        </span>
        <div>
          <h1 className="font-display text-2xl text-haiti-blue">Carte d'Haiti</h1>
          <p className="text-sm text-slate-500">Choisis un departement pour commencer ton aventure.</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {departments.map((dept, index) => {
          const deptProgress = progress.find((p) => p.department === dept.id);
          return (
            <motion.div
              key={dept.id}
              initial={{ opacity: 0, scale: 0.8, y: 12 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ delay: index * 0.04, type: "spring", stiffness: 300, damping: 20 }}
            >
              <Link
                to={`/aventure/${dept.id}`}
                className="card-game flex flex-col items-center gap-1 py-5 text-center transition-all duration-150 hover:-translate-y-1 hover:shadow-card-hover active:translate-y-0.5"
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
