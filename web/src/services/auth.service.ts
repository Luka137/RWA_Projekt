import api from "./api";
import type { TokenResponse, User } from "@/types";

export const authService = {
  // POST /auth/login -> { access_token, refresh_token, token_type }
  async login(username: string, password: string): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/login", {
      username,
      password,
    });
    return data;
  },

  // GET /auth/me -> trenutni korisnik (na temelju access tokena)
  async me(): Promise<User> {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },

  // POST /users/register -> registracija novog clana
  async register(username: string, password: string): Promise<User> {
    const { data } = await api.post<User>("/users/register", {
      username,
      password,
    });
    return data;
  },
};
