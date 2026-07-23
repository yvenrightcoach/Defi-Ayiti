import { isAxiosError } from "axios";

export function getErrorMessage(error: unknown, fallback = "Une erreur est survenue."): string {
  if (isAxiosError(error)) {
    const data = error.response?.data;
    if (typeof data === "string") return data;
    if (data && typeof data === "object") {
      const firstValue = Object.values(data as Record<string, unknown>)[0];
      if (Array.isArray(firstValue)) return String(firstValue[0]);
      if (typeof firstValue === "string") return firstValue;
      if ("detail" in data && typeof (data as { detail?: unknown }).detail === "string") {
        return (data as { detail: string }).detail;
      }
    }
  }
  return fallback;
}
