import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { Question } from "@/types/api";

import QuestionCard from "./QuestionCard";

const question: Question = {
  id: "q1",
  category: "cat1",
  department: null,
  level: null,
  question_type: "multiple_choice",
  difficulty: "easy",
  text: "En quelle annee Haiti a-t-il obtenu son independance ?",
  image: "",
  xp_reward: 10,
  is_boss_question: false,
  answers: [
    { id: "a1", text: "1804", image: "", order: 0 },
    { id: "a2", text: "1789", image: "", order: 1 },
  ],
};

describe("QuestionCard", () => {
  it("renders the question text and all answers", () => {
    render(<QuestionCard question={question} selectedIds={[]} onToggle={vi.fn()} result={null} multiSelect={false} />);
    expect(screen.getByText(question.text)).toBeInTheDocument();
    expect(screen.getByText("1804")).toBeInTheDocument();
    expect(screen.getByText("1789")).toBeInTheDocument();
  });

  it("calls onToggle with the answer id when clicked", async () => {
    const onToggle = vi.fn();
    render(<QuestionCard question={question} selectedIds={[]} onToggle={onToggle} result={null} multiSelect={false} />);
    await userEvent.click(screen.getByText("1804"));
    expect(onToggle).toHaveBeenCalledWith("a1");
  });

  it("disables answers once a result is available", () => {
    render(
      <QuestionCard
        question={question}
        selectedIds={["a1"]}
        onToggle={vi.fn()}
        result={{ is_correct: true, correct_answer_ids: ["a1"], explanation: "1804.", xp_awarded: 10 }}
        multiSelect={false}
      />,
    );
    expect(screen.getByText("1804").closest("button")).toBeDisabled();
    expect(screen.getByText(/Bonne reponse/)).toBeInTheDocument();
    expect(screen.getByText("1804.")).toBeInTheDocument();
  });

  it("shows an incorrect message when the answer is wrong", () => {
    render(
      <QuestionCard
        question={question}
        selectedIds={["a2"]}
        onToggle={vi.fn()}
        result={{ is_correct: false, correct_answer_ids: ["a1"], explanation: "1804.", xp_awarded: 0 }}
        multiSelect={false}
      />,
    );
    expect(screen.getByText(/Pas tout a fait/)).toBeInTheDocument();
  });
});
