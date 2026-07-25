import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useInstallPrompt } from "@/hooks/useInstallPrompt";

function mockMatchMedia(matches: boolean) {
  window.matchMedia = vi.fn().mockReturnValue({ matches }) as unknown as typeof window.matchMedia;
}

function mockUserAgent(ua: string) {
  Object.defineProperty(window.navigator, "userAgent", { value: ua, configurable: true });
}

describe("useInstallPrompt", () => {
  beforeEach(() => {
    mockMatchMedia(false);
    mockUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("captures the beforeinstallprompt event and exposes canInstall", () => {
    const { result } = renderHook(() => useInstallPrompt());
    expect(result.current.canInstall).toBe(false);

    const event = Object.assign(new Event("beforeinstallprompt"), {
      prompt: vi.fn(),
      userChoice: Promise.resolve({ outcome: "accepted" as const }),
    });
    const preventDefault = vi.spyOn(event, "preventDefault");

    act(() => {
      window.dispatchEvent(event);
    });

    expect(preventDefault).toHaveBeenCalled();
    expect(result.current.canInstall).toBe(true);
  });

  it("promptInstall triggers the captured event and resets canInstall", async () => {
    const { result } = renderHook(() => useInstallPrompt());
    const prompt = vi.fn();
    const event = Object.assign(new Event("beforeinstallprompt"), {
      prompt,
      userChoice: Promise.resolve({ outcome: "accepted" as const }),
    });

    act(() => {
      window.dispatchEvent(event);
    });
    expect(result.current.canInstall).toBe(true);

    await act(async () => {
      await result.current.promptInstall();
    });

    expect(prompt).toHaveBeenCalled();
    expect(result.current.canInstall).toBe(false);
  });

  it("detects iOS from the user agent when beforeinstallprompt never fires", () => {
    mockUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15");
    const { result } = renderHook(() => useInstallPrompt());
    expect(result.current.isIOS).toBe(true);
    expect(result.current.canInstall).toBe(false);
  });

  it("does not report iOS on a regular desktop Chrome user agent", () => {
    const { result } = renderHook(() => useInstallPrompt());
    expect(result.current.isIOS).toBe(false);
  });

  it("reports isStandalone when display-mode is already standalone", () => {
    mockMatchMedia(true);
    const { result } = renderHook(() => useInstallPrompt());
    expect(result.current.isStandalone).toBe(true);
  });
});
