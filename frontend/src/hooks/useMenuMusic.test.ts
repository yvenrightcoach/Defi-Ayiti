import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { playMenuMusic, stopMenuMusic } from "@/lib/sound";
import { useMenuMusic } from "@/hooks/useMenuMusic";

vi.mock("@/lib/sound", () => ({
  playMenuMusic: vi.fn(),
  stopMenuMusic: vi.fn(),
}));

describe("useMenuMusic", () => {
  it("plays on regular pages", () => {
    renderHook(() => useMenuMusic("/aventure"));
    expect(playMenuMusic).toHaveBeenCalled();
    expect(stopMenuMusic).not.toHaveBeenCalled();
  });

  it("stays silent during a quiz", () => {
    vi.clearAllMocks();
    renderHook(() => useMenuMusic("/quiz/level/3"));
    expect(stopMenuMusic).toHaveBeenCalled();
    expect(playMenuMusic).not.toHaveBeenCalled();
  });

  it("stays silent during a battle", () => {
    vi.clearAllMocks();
    renderHook(() => useMenuMusic("/battle"));
    expect(stopMenuMusic).toHaveBeenCalled();
    expect(playMenuMusic).not.toHaveBeenCalled();
  });

  it("resumes when leaving a quiz for another page", () => {
    vi.clearAllMocks();
    const { rerender } = renderHook(({ pathname }) => useMenuMusic(pathname), {
      initialProps: { pathname: "/quiz" },
    });
    expect(stopMenuMusic).toHaveBeenCalledTimes(1);

    rerender({ pathname: "/aventure" });
    expect(playMenuMusic).toHaveBeenCalledTimes(1);
  });
});
