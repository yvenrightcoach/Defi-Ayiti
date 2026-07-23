import { beforeEach, describe, expect, it } from "vitest";

import { useAuthStore } from "./authStore";

const SESSION = {
  user: { id: "u1", username: "joueur1", isGuest: true },
  accessToken: "access-token",
  refreshToken: "refresh-token",
};

describe("authStore", () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, accessToken: null, refreshToken: null });
    localStorage.clear();
  });

  it("starts with no session", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
  });

  it("stores the session on setSession", () => {
    useAuthStore.getState().setSession(SESSION);
    const state = useAuthStore.getState();
    expect(state.user).toEqual(SESSION.user);
    expect(state.accessToken).toBe("access-token");
    expect(state.refreshToken).toBe("refresh-token");
  });

  it("clears the session on logout", () => {
    useAuthStore.getState().setSession(SESSION);
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
  });

  it("persists the session to localStorage", () => {
    useAuthStore.getState().setSession(SESSION);
    const stored = JSON.parse(localStorage.getItem("defi-ayiti-auth") ?? "{}");
    expect(stored.state.accessToken).toBe("access-token");
  });
});
