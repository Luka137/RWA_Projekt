import api from "./api";
import type { Membership, MembershipCreatePayload } from "@/types";

export const membershipService = {
  // GET /memberships  (vlastite ako member, sve ako admin)
  async list(): Promise<Membership[]> {
    const { data } = await api.get<Membership[]>("/memberships");
    return data;
  },

  // GET /memberships/{id}
  async get(id: number): Promise<Membership> {
    const { data } = await api.get<Membership>(`/memberships/${id}`);
    return data;
  },

  // POST /memberships  (admin)
  async create(payload: MembershipCreatePayload): Promise<Membership> {
    const { data } = await api.post<Membership>("/memberships", payload);
    return data;
  },

  // PATCH /memberships/{id}/cancel
  async cancel(id: number): Promise<Membership> {
    const { data } = await api.patch<Membership>(`/memberships/${id}/cancel`);
    return data;
  },
};
