import { useEffect, useRef, useState } from "react";
import { AnimatePresence } from "framer-motion";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import QuestionCard from "@/features/quiz/QuestionCard";
import { getErrorMessage } from "@/lib/errors";
import {
  createRoom,
  finishMatch,
  getRoom,
  joinRoom,
  startMatch,
  submitMatchScore,
} from "@/services/endpoints/battles";
import { listCategories, getQuestionsByIds, submitAnswer } from "@/services/endpoints/quiz";
import { useProfileStore } from "@/store/profileStore";
import type { AnswerResult, BattleRoom, Category, Question } from "@/types/api";

type BattleStep = "lobby" | "room" | "playing" | "waiting" | "finished";

export default function BattlePage() {
  const { profile, refresh } = useProfileStore();
  const [step, setStep] = useState<BattleStep>("lobby");
  const [room, setRoom] = useState<BattleRoom | null>(null);
  const [joinCode, setJoinCode] = useState("");
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [qIndex, setQIndex] = useState(0);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const pollRef = useRef<number | null>(null);
  const loadedMatchIdRef = useRef<string | null>(null);

  useEffect(() => {
    void listCategories().then(setCategories);
    if (!profile) void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  function startPolling(roomId: string) {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      try {
        const updated = await getRoom(roomId);
        setRoom(updated);

        const latestMatch = updated.matches[updated.matches.length - 1];
        if (updated.status === "in_progress" && latestMatch && loadedMatchIdRef.current !== latestMatch.id) {
          loadedMatchIdRef.current = latestMatch.id;
          const fullQuestions = await getQuestionsByIds(latestMatch.questions);
          setQuestions(fullQuestions);
          setQIndex(0);
          setCorrectCount(0);
          setSelectedIds([]);
          setResult(null);
          setStep("playing");
        }
        if (updated.status === "finished") {
          setStep((current) => (current === "finished" ? current : "finished"));
        }
      } catch {
        // silencieux : on reessaiera au prochain tick
      }
    }, 3000);
  }

  async function handleCreateRoom() {
    setIsBusy(true);
    setError(null);
    try {
      const newRoom = await createRoom("friend", 2);
      setRoom(newRoom);
      setStep("room");
      startPolling(newRoom.id);
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de creer la salle."));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleJoinRoom(event: React.FormEvent) {
    event.preventDefault();
    setIsBusy(true);
    setError(null);
    try {
      const joined = await joinRoom(joinCode.trim().toUpperCase());
      setRoom(joined);
      setStep("room");
      startPolling(joined.id);
    } catch (err) {
      setError(getErrorMessage(err, "Code de salle invalide."));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleStartMatch() {
    if (!room) return;
    setIsBusy(true);
    setError(null);
    try {
      const match = await startMatch(room.id, { category: selectedCategory || undefined, question_count: 5 });
      loadedMatchIdRef.current = match.id;
      const fullQuestions = await getQuestionsByIds(match.questions);
      setQuestions(fullQuestions);
      setQIndex(0);
      setCorrectCount(0);
      setSelectedIds([]);
      setResult(null);
      setStep("playing");
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de lancer la partie."));
    } finally {
      setIsBusy(false);
    }
  }

  function toggleAnswer(answerId: string) {
    if (result) return;
    setSelectedIds([answerId]);
  }

  async function handleValidate() {
    const question = questions[qIndex];
    if (!question || selectedIds.length === 0) return;
    setIsBusy(true);
    try {
      const res = await submitAnswer(question.id, selectedIds);
      setResult(res);
      if (res.is_correct) setCorrectCount((c) => c + 1);
    } catch (err) {
      setError(getErrorMessage(err, "Impossible d'envoyer ta reponse."));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleNextQuestion() {
    if (qIndex + 1 < questions.length) {
      setQIndex((i) => i + 1);
      setSelectedIds([]);
      setResult(null);
      return;
    }
    // Fin des questions pour ce joueur
    if (room?.matches?.length) {
      const latestMatch = room.matches[room.matches.length - 1];
      const scorePercent = Math.round((correctCount / questions.length) * 100);
      await submitMatchScore(latestMatch.id, scorePercent, correctCount);
      await refresh();
    }
    setStep("waiting");
    if (room) startPolling(room.id);
  }

  async function handleFinishMatch() {
    if (!room?.matches?.length) return;
    setIsBusy(true);
    try {
      const latestMatch = room.matches[room.matches.length - 1];
      await finishMatch(latestMatch.id);
      const updated = await getRoom(room.id);
      setRoom(updated);
      setStep("finished");
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de cloturer le match."));
    } finally {
      setIsBusy(false);
    }
  }

  function reset() {
    if (pollRef.current) window.clearInterval(pollRef.current);
    setRoom(null);
    setStep("lobby");
    setQuestions([]);
  }

  const isHost = room?.host.id === profile?.id;

  return (
    <section className="min-h-screen bg-haiti-blue/5 p-4">
      <h1 className="mb-4 text-2xl font-display text-haiti-blue">Battle</h1>
      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {step === "lobby" && (
        <div className="space-y-4">
          <button type="button" onClick={handleCreateRoom} disabled={isBusy} className="btn-game-primary w-full">
            Creer une battle entre amis
          </button>
          <form onSubmit={handleJoinRoom} className="card-game space-y-2">
            <p className="font-display text-haiti-blue">Rejoindre avec un code</p>
            <input
              type="text"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value)}
              placeholder="Ex: WX30Q6"
              className="w-full rounded-pill border border-slate-200 px-4 py-2 text-center uppercase tracking-widest outline-none focus:border-haiti-blue"
            />
            <button type="submit" disabled={isBusy || !joinCode} className="btn-game-secondary w-full">
              Rejoindre
            </button>
          </form>
        </div>
      )}

      {step === "room" && room && (
        <div className="card-game space-y-3 text-center">
          <p className="text-sm text-slate-500">Code de la salle</p>
          <p className="text-3xl font-display tracking-widest text-haiti-blue">{room.room_code}</p>
          <div className="space-y-1">
            {room.participants.map((p) => (
              <p key={p.id}>👤 {p.user.username}</p>
            ))}
          </div>
          {isHost ? (
            <div className="space-y-2">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full rounded-pill border border-slate-200 px-4 py-2"
              >
                <option value="">Toutes les categories</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={handleStartMatch}
                disabled={isBusy || room.participants.length < 2}
                className="btn-game-primary w-full disabled:opacity-50"
              >
                {room.participants.length < 2 ? "En attente d'un adversaire..." : "Lancer la partie"}
              </button>
            </div>
          ) : (
            <p className="text-slate-500">En attente que l'hote lance la partie...</p>
          )}
          <button type="button" onClick={reset} className="text-sm text-slate-400 underline">
            Annuler
          </button>
        </div>
      )}

      {step === "playing" && questions[qIndex] && (
        <div>
          <p className="mb-3 text-sm text-slate-500">
            Question {qIndex + 1}/{questions.length}
          </p>
          <AnimatePresence mode="wait">
            <QuestionCard
              key={questions[qIndex].id}
              question={questions[qIndex]}
              selectedIds={selectedIds}
              onToggle={toggleAnswer}
              result={result}
              multiSelect={false}
            />
          </AnimatePresence>
          <div className="mt-4">
            {!result ? (
              <button
                type="button"
                onClick={handleValidate}
                disabled={selectedIds.length === 0 || isBusy}
                className="btn-game-primary w-full disabled:opacity-50"
              >
                Valider
              </button>
            ) : (
              <button type="button" onClick={handleNextQuestion} className="btn-game-secondary w-full">
                {qIndex + 1 < questions.length ? "Suivant" : "Terminer mes reponses"}
              </button>
            )}
          </div>
        </div>
      )}

      {step === "waiting" && room && (
        <div className="card-game text-center">
          <Loader label="En attente des autres joueurs..." />
          <p className="mb-3 text-sm text-slate-500">
            {correctCount}/{questions.length} bonnes reponses
          </p>
          {isHost && (
            <button type="button" onClick={handleFinishMatch} disabled={isBusy} className="btn-game-primary w-full">
              Cloturer le match
            </button>
          )}
        </div>
      )}

      {step === "finished" && room?.matches?.length && (
        <div className="card-game text-center">
          <h2 className="text-xl font-display text-haiti-blue">Match termine !</h2>
          <div className="mt-3 space-y-2">
            {[...room.matches[room.matches.length - 1].participants]
              .sort((a, b) => (a.rank ?? 99) - (b.rank ?? 99))
              .map((participant) => (
                <p key={participant.id}>
                  {participant.rank === 1 ? "🏆 " : ""}
                  {participant.profile.user.username} — {participant.score} pts
                </p>
              ))}
          </div>
          <button type="button" onClick={reset} className="btn-game-primary mt-4 w-full">
            Nouvelle partie
          </button>
        </div>
      )}
    </section>
  );
}
