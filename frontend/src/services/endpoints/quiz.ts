import { apiClient } from "@/services/apiClient";
import type { AnswerResult, Category, Paginated, Question } from "@/types/api";

export async function listCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<Paginated<Category>>("/quiz/categories/", { params: { page_size: 20 } });
  return data.results;
}

export async function listQuestions(filters: { level?: string; category?: string; department?: string }) {
  const { data } = await apiClient.get<Paginated<Question>>("/quiz/questions/", {
    params: { page_size: 50, ...filters },
  });
  return data.results;
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
