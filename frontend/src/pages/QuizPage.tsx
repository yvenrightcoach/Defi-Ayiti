import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Confetti from "react-confetti";
import { useNavigate, useParams } from "react-router-dom";

import AnimatedBackground from "@/components/ui/AnimatedBackground";
import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import Mascot from "@/components/ui/Mascot";
import QuestionCard from "@/features/quiz/QuestionCard";
import { useCountUp } from "@/hooks/useCountUp";
import { getErrorMessage } from "@/lib/errors";
import { playCorrect, playSuccess, playUnlock, playWrong } from "@/lib/sound";
import { completeLevel } from "@/services/endpoints/progress";
import { listQuestions, submitAnswer } from "@/services/endpoints/quiz";
import { useProfileStore } from "@/store/profileStore";
import type { AnswerResult, CompleteLevelResult, Question } from "@/types/api";

export default function QuizPage() {
  const { levelId } = useParams<{ levelId?: string }>();
  const navigate = useNavigate();
  const refreshProfile = useProfileStore((state) => state.refresh);

  const [questions, setQuestions] = useState<Question[]>([]);
  const [index, setIndex] = useState(0);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [totalXp, setTotalXp] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [levelResult, setLevelResult] = useState<CompleteLevelResult | null>(null);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await listQuestions(levelId ? { level: levelId } : {});
        setQuestions(data.slice(0, levelId ? data.length : 5));
      } catch (err) {
        setError(getErrorMessage(err, "Impossible de charger les questions."));
      } finally {
        setIsLoading(false);
      }
    }
    void load();
  }, [levelId]);

  const currentQuestion = questions[index];
  const multiSelect = currentQuestion?.question_type === "matching" || currentQuestion?.question_type === "timeline";

  function toggleAnswer(answerId: string) {
    if (result) return;
    if (multiSelect) {
      setSelectedIds((prev) =>
        prev.includes(answerId) ? prev.filter((id) => id !== answerId) : [...prev, answerId],
      );
    } else {
      setSelectedIds([answerId]);
    }
  }

  async function handleValidate() {
    if (!currentQuestion || selectedIds.length === 0) return;
    setIsSubmitting(true);
    try {
      const res = await submitAnswer(currentQuestion.id, selectedIds);
      setResult(res);
      if (res.is_correct) {
        setCorrectCount((c) => c + 1);
        setTotalXp((xp) => xp + res.xp_awarded);
        playCorrect();
      } else {
        playWrong();
      }
    } catch (err) {
      setError(getErrorMessage(err, "Impossible d'envoyer ta reponse."));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleNext() {
    if (index + 1 < questions.length) {
      setIndex((i) => i + 1);
      setSelectedIds([]);
      setResult(null);
      return;
    }

    // Fin du quiz
    if (levelId) {
      const scorePercent = Math.round((correctCount / questions.length) * 100);
      try {
        const res = await completeLevel(levelId, scorePercent);
        setLevelResult(res);
      } catch (err) {
        setError(getErrorMessage(err, "Impossible de valider le chapitre."));
      }
    }
    await refreshProfile();
    setFinished(true);
  }

  if (isLoading) return <Loader label="Preparation du quiz..." />;
  if (error && !finished) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;
  if (questions.length === 0) {
    return (
      <div className="min-h-screen p-4">
        <ErrorMessage message="Aucune question disponible pour le moment." />
      </div>
    );
  }

  if (finished) {
    return (
      <FinishScreen
        correctCount={correctCount}
        total={questions.length}
        totalXp={totalXp}
        levelResult={levelResult}
        onContinue={() => navigate(levelId ? `/aventure` : "/")}
      />
    );
  }

  return (
    <section className="min-h-screen p-4">
      <div className="mb-2 flex items-center justify-between text-sm font-display text-slate-500">
        <span>
          Question {index + 1}/{questions.length}
        </span>
        <span className="text-haiti-green">✓ {correctCount} bonnes reponses</span>
      </div>
      <div className="mb-4 h-4 overflow-hidden rounded-pill border-2 border-haiti-blue/10 bg-white">
        <motion.div
          className="h-full rounded-pill bg-haiti-green"
          animate={{ width: `${((index + (result ? 1 : 0)) / questions.length) * 100}%` }}
          transition={{ type: "spring", stiffness: 200, damping: 25 }}
        />
      </div>

      <AnimatePresence mode="wait">
        <QuestionCard
          key={currentQuestion.id}
          question={currentQuestion}
          selectedIds={selectedIds}
          onToggle={toggleAnswer}
          result={result}
          multiSelect={multiSelect}
        />
      </AnimatePresence>

      <div className="mt-4">
        {!result ? (
          <button
            type="button"
            onClick={handleValidate}
            disabled={selectedIds.length === 0 || isSubmitting}
            className="btn-game-primary w-full disabled:opacity-50"
          >
            {isSubmitting ? "Verification..." : "Valider"}
          </button>
        ) : (
          <button type="button" onClick={handleNext} className="btn-game-secondary w-full">
            {index + 1 < questions.length ? "Question suivante" : "Voir le resultat"}
          </button>
        )}
      </div>
    </section>
  );
}

function FinishScreen({
  correctCount,
  total,
  totalXp,
  levelResult,
  onContinue,
}: {
  correctCount: number;
  total: number;
  totalXp: number;
  levelResult: CompleteLevelResult | null;
  onContinue: () => void;
}) {
  const passed = levelResult ? levelResult.level_passed : correctCount / total >= 0.5;
  const heroUnlocked = levelResult?.hero_unlocked ?? null;
  const xpDisplay = useCountUp(levelResult?.xp_awarded ?? totalXp);
  const coinDisplay = useCountUp(levelResult?.coin_awarded ?? 0);

  useEffect(() => {
    if (heroUnlocked) {
      playUnlock();
    } else if (passed) {
      playSuccess();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center text-white">
      <AnimatedBackground variant="dark" />
      {(passed || heroUnlocked) && (
        <Confetti numberOfPieces={heroUnlocked ? 300 : 150} recycle={false} width={window.innerWidth} height={window.innerHeight} />
      )}
      <motion.div
        initial={{ scale: 0.3, opacity: 0, y: 40 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 18 }}
        className="relative z-10 w-full max-w-sm"
      >
        <Mascot className={`mx-auto h-24 w-24 drop-shadow-xl ${passed ? "animate-float" : ""}`} />
        <h1 className="text-toon text-4xl">{passed ? "Bravo !" : "Presque !"}</h1>
        <p className="mt-2 text-haiti-yellow">
          {correctCount}/{total} bonnes reponses
        </p>

        <div className="card-game mt-4 text-slate-800">
          <p className="font-display text-haiti-blue">+{xpDisplay} XP</p>
          {levelResult && <p className="font-display text-haiti-blue">+{coinDisplay} pieces</p>}
        </div>

        {heroUnlocked && (
          <motion.div
            initial={{ scale: 0, rotate: -10 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", delay: 0.3 }}
            className="card-game mt-4 animate-pop-in text-slate-800"
          >
            <p className="font-display text-haiti-yellow">Heros debloque !</p>
            <p className="text-lg font-display text-haiti-blue">{heroUnlocked.name}</p>
            {heroUnlocked.quote && <p className="mt-1 text-sm italic text-slate-500">"{heroUnlocked.quote}"</p>}
          </motion.div>
        )}

        <button type="button" onClick={onContinue} className="btn-game-primary mt-6 w-full">
          Continuer
        </button>
      </motion.div>
    </section>
  );
}
