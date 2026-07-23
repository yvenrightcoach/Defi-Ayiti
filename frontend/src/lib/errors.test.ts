import { describe, expect, it } from "vitest";

import { getErrorMessage } from "./errors";

function axiosErrorWith(data: unknown) {
  return { isAxiosError: true, response: { data } };
}

describe("getErrorMessage", () => {
  it("returns the fallback for a non-axios error", () => {
    expect(getErrorMessage(new Error("boom"))).toBe("Une erreur est survenue.");
  });

  it("returns a custom fallback when provided", () => {
    expect(getErrorMessage(new Error("boom"), "Oups.")).toBe("Oups.");
  });

  it("returns the fallback when the axios error has no response", () => {
    expect(getErrorMessage({ isAxiosError: true })).toBe("Une erreur est survenue.");
  });

  it("returns a plain string response body as-is", () => {
    expect(getErrorMessage(axiosErrorWith("Erreur serveur"))).toBe("Erreur serveur");
  });

  it("returns the first item of a DRF field-error array", () => {
    const error = axiosErrorWith({ username: ["Ce champ est requis."] });
    expect(getErrorMessage(error)).toBe("Ce champ est requis.");
  });

  it("returns a DRF 'detail' message", () => {
    const error = axiosErrorWith({ detail: "Non trouve." });
    expect(getErrorMessage(error)).toBe("Non trouve.");
  });
});
