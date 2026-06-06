import api from "./api";
import type {
  Training,
  TrainingCreatePayload,
  TrainingUpdatePayload,
} from "@/types";

export const trainingService = {
  // GET /trainings
  async list(): Promise<Training[]> {
    const { data } = await api.get<Training[]>("/trainings");
    return data;
  },

  // GET /trainings/{id}
  async get(id: number): Promise<Training> {
    const { data } = await api.get<Training>(`/trainings/${id}`);
    return data;
  },

  // POST /trainings  (admin, trainer)
  async create(payload: TrainingCreatePayload): Promise<Training> {
    const { data } = await api.post<Training>("/trainings", payload);
    return data;
  },

  // PATCH /trainings/{id}  (admin, owner)
  async update(id: number, payload: TrainingUpdatePayload): Promise<Training> {
    const { data } = await api.patch<Training>(`/trainings/${id}`, payload);
    return data;
  },

  // PATCH /trainings/{id}/start
  async start(id: number): Promise<Training> {
    const { data } = await api.patch<Training>(`/trainings/${id}/start`);
    return data;
  },

  // PATCH /trainings/{id}/complete
  async complete(id: number): Promise<Training> {
    const { data } = await api.patch<Training>(`/trainings/${id}/complete`);
    return data;
  },

  // PATCH /trainings/{id}/cancel
  async cancel(id: number): Promise<Training> {
    const { data } = await api.patch<Training>(`/trainings/${id}/cancel`);
    return data;
  },
};
