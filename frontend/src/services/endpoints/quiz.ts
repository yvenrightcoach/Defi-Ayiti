import { apiClient } from "@/services/apiClient";
import type { AnswerResult, Category, Paginated, Question } from "@/types/api";

export async function listCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<Paginated<Category>>("/quiz/categories/", { params: { page_size: 20 } });
  return data.results;
}

/**
 * Tire des questions aleatoires pour une session de jeu : l'ordre et la
 * selection changent a chaque appel, pour plus de difficulte. Le nombre de
 * questions (50 pour un chapitre d'aventure, 30 sinon) est decide cote
 * serveur.
 */
export async function listQuestionSession(filters: {
  level?: string;
  category?: string;
  department?: string;
}): Promise<Question[]> {
  const { data } = await apiClient.get<Question[]>("/quiz/questions/session/", { params: filters });
  return data;
}

export async function submitAnswer(questionId: string, answerIds: string[]): Promise<AnswerResult> {
  const { data } = await apiClient.post<AnswerResult>(`/quiz/questions/${questionId}/submit/`, {
    answer_ids: answerIds,
  });
  return data;
}

export async function getQuestion(id: string): Promise<Question> {
  const { data } = await apiClient.get<Question>(`/quiz/questions/${id}/`);
  return data;
}

export async function getQuestionsByIds(ids: string[]): Promise<Question[]> {
  return Promise.all(ids.map((id) => getQuestion(id)));
}
