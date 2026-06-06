import api from "./api";
import type { Reservation } from "@/types";

// Rezervacije su ugnijezdene pod treningom:
// /trainings/{training_id}/reservations
export const reservationService = {
  // GET /trainings/{id}/reservations
  async list(trainingId: number): Promise<Reservation[]> {
    const { data } = await api.get<Reservation[]>(
      `/trainings/${trainingId}/reservations`,
    );
    return data;
  },

  // POST /trainings/{id}/reservations  (member, treba aktivna clanarina)
  async create(trainingId: number): Promise<Reservation> {
    const { data } = await api.post<Reservation>(
      `/trainings/${trainingId}/reservations`,
    );
    return data;
  },

  // DELETE /trainings/{id}/reservations/{rid}  (self, trainer, admin) -> 204
  async cancel(trainingId: number, reservationId: number): Promise<void> {
    await api.delete(
      `/trainings/${trainingId}/reservations/${reservationId}`,
    );
  },
};
