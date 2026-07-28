import { create } from "zustand";
import axios from "axios";
import type { User } from "../api/auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost/api";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setSession: (access: string, refresh: string, user: User) => void;
  refreshAccessToken: () => Promise<boolean>;
  logout: () => void;
}

// In-memory only — no localStorage. A page refresh requires logging in
// again via OTP, which is an acceptable tradeoff for a payments app.
export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  refreshToken: null,
  user: null,

  setSession: (access, refresh, user) =>
    set({ accessToken: access, refreshToken: refresh, user }),

  refreshAccessToken: async () => {
    const refresh = get().refreshToken;
    if (!refresh) return false;
    try {
      const { data } = await axios.post(`${API_BASE_URL}/accounts/token/refresh/`, {
        refresh,
      });
      set({ accessToken: data.access });
      return true;
    } catch {
      return false;
    }
  },

  logout: () => set({ accessToken: null, refreshToken: null, user: null }),
}));