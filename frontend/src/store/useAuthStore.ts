import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  role: string | null;
  isAuthenticated: boolean;
  setAuth: (accessToken: string, refreshToken: string, role: string) => void;
  updateTokens: (accessToken: string, refreshToken: string, role: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      role: null,
      isAuthenticated: false,

      setAuth: (accessToken, refreshToken, role) =>
        set({
          accessToken,
          refreshToken,
          role,
          isAuthenticated: true,
        }),

      updateTokens: (accessToken, refreshToken, role) =>
        set({
          accessToken,
          refreshToken,
          role,
        }),

      logout: () =>
        set({
          accessToken: null,
          refreshToken: null,
          role: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'auth-storage', 
    }
  )
);