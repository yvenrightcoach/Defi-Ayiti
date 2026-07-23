import { motion } from "framer-motion";

import type { AnswerResult, Question } from "@/types/api";

interface QuestionCardProps {
  question: Question;
  selectedIds: string[];
  onToggle: (answerId: string) => void;
  result: AnswerResult | null;
  multiSelect: boolean;
}

export default function QuestionCard({ question, selectedIds, onToggle, result, multiSelect }: QuestionCardProps) {
  return (
    <motion.div
      key={question.id}
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -24 }}
      transition={{ duration: 0.25 }}
      className="card-game"
    >
      <p className="mb-1 text-xs font-display uppercase tracking-wide text-haiti-blue/60">
        {question.question_type === "true_false" ? "Vrai ou faux" : "Choix multiple"}
      </p>
      <h2 className="mb-4 text-lg font-display text-haiti-blue">{question.text}</h2>
      {question.image && (
        <img src={question.image} alt="" className="mb-4 max-h-48 w-full rounded-card object-cover" />
      )}

      <div className="space-y-2">
        {question.answers.map((answer, i) => {
          const isSelected = selectedIds.includes(answer.id);
          const isCorrectAnswer = result?.correct_answer_ids.includes(answer.id);
          const showResult = result !== null;
          const letter = String.fromCharCode(65 + i);

          let stateClasses = "border-slate-200 hover:border-haiti-blue hover:-translate-y-0.5";
          let badgeClasses = "bg-slate-100 text-slate-500";
          if (showResult && isCorrectAnswer) {
            stateClasses = "border-haiti-green bg-haiti-green/10";
            badgeClasses = "bg-haiti-green text-white";
          } else if (showResult && isSelected && !isCorrectAnswer) {
            stateClasses = "border-haiti-red bg-haiti-red/10";
            badgeClasses = "bg-haiti-red text-white";
          } else if (isSelected) {
            stateClasses = "border-haiti-blue bg-haiti-blue/5";
            badgeClasses = "bg-haiti-blue text-white";
          }

          return (
            <button
              key={answer.id}
              type="button"
              disabled={showResult}
              onClick={() => onToggle(answer.id)}
              className={`flex w-full items-center gap-3 rounded-card border-2 p-3 text-left font-display transition-all duration-150 active:translate-y-0 ${stateClasses}`}
            >
              <span
                className={`flex h-8 w-8 shrink-0 items-center justify-center text-sm transition-colors ${
                  multiSelect ? "rounded-lg" : "rounded-full"
                } ${badgeClasses}`}
              >
                {showResult && isCorrectAnswer ? "✓" : showResult && isSelected ? "✕" : letter}
              </span>
              <span className="text-slate-700">{answer.text}</span>
            </button>
          );
        })}
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-4 rounded-card p-3 text-sm ${
            result.is_correct ? "bg-haiti-green/10 text-haiti-green" : "bg-haiti-red/10 text-haiti-red"
          }`}
        >
          <p className="font-display">
            {result.is_correct ? `Bonne reponse ! +${result.xp_awarded} XP` : "Pas tout a fait..."}
          </p>
          {result.explanation && <p className="mt-1 text-slate-600">{result.explanation}</p>}
        </motion.div>
      )}
    </motion.div>
  );
}
