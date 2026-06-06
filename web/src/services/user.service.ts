import api from "./api";
import type { User } from "@/types";

export const userService = {
  // GET /users  (admin)
  async list(): Promise<User[]> {
    const { data } = await api.get<User[]>("/users");
    return data;
  },

  // GET /users/{id}  (self ili admin)
  async get(id: number): Promise<User> {
    const { data } = await api.get<User>(`/users/${id}`);
    return data;
  },
};
