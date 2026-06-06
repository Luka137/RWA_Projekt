import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";
import type { ApiError } from "@/types";

// Bazni URL: u produkciji iz env varijable, u dev-u prazno -> Vite proxy hvata /api.
const BASE_URL = import.meta.env.VITE_API_URL || "/api";

// Kljucevi pod kojima cuvamo tokene u localStorage.
const ACCESS_KEY = "gym_access_token";
const REFRESH_KEY = "gym_refresh_token";

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  set: (access: string, refresh: string) => {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

// Glavna axios instanca koju koriste svi servisi.
const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// --- REQUEST INTERCEPTOR ---
// Prije svakog requesta zalijepi Authorization header ako imamo access token.
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- RESPONSE INTERCEPTOR (auto-refresh) ---
// Access token traje samo 15 min. Kad istekne, backend vraca 401.
// Tada pokusamo jednom osvjeziti token preko /auth/refresh i ponoviti zahtjev.
// Ako i refresh padne -> brisemo tokene i saljemo korisnika na login.

let isRefreshing = false;
// Red zahtjeva koji cekaju da refresh zavrsi (da ne saljemo 5 refresh poziva odjednom).
let pendingQueue: Array<(token: string | null) => void> = [];

function flushQueue(token: string | null) {
  pendingQueue.forEach((cb) => cb(token));
  pendingQueue = [];
}

// Callback koji router postavi - poziva se kad refresh definitivno ne uspije.
let onAuthFailure: (() => void) | null = null;
export function setAuthFailureHandler(fn: () => void) {
  onAuthFailure = fn;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean;
    };

    const status = error.response?.status;
    const isRefreshCall = originalRequest.url?.includes("/auth/refresh");

    // Reagiramo samo na 401, i to ne na sam refresh poziv, i samo jednom po zahtjevu.
    if (status === 401 && !originalRequest._retry && !isRefreshCall) {
      const refreshToken = tokenStorage.getRefresh();

      if (!refreshToken) {
        tokenStorage.clear();
        onAuthFailure?.();
        return Promise.reject(error);
      }

      // Ako se vec osvjezava, sacekaj u redu pa ponovi s novim tokenom.
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push((newToken) => {
            if (newToken) {
              originalRequest.headers = originalRequest.headers ?? {};
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              resolve(api(originalRequest));
            } else {
              reject(error);
            }
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Vazno: koristimo cisti axios (ne nasu instancu) da ne udemo u petlju interceptora.
        const { data } = await axios.post<{
          access_token: string;
          refresh_token: string;
        }>(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });

        tokenStorage.set(data.access_token, data.refresh_token);
        flushQueue(data.access_token);

        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token istekao ili nevazeci -> odjava.
        flushQueue(null);
        tokenStorage.clear();
        onAuthFailure?.();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

// Pomocna funkcija: izvuci citljivu poruku greske iz backend odgovora.
export function extractErrorMessage(error: unknown, fallback = "Došlo je do greške"): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiError | undefined;
    if (data?.message) return data.message;
    if (error.message) return error.message;
  }
  return fallback;
}

export default api;
