import type {
  TrainingStatus,
  ReservationStatus,
  MembershipStatus,
  Role,
} from "@/types";

// Formatira ISO datetime u citljiv hrvatski format: "12.06.2026. u 18:30"
export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const date = d.toLocaleDateString("hr-HR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
  const time = d.toLocaleTimeString("hr-HR", {
    hour: "2-digit",
    minute: "2-digit",
  });
  return `${date} u ${time}`;
}

// Formatira samo datum (za clanarine): "12.06.2026."
export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("hr-HR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

// Pretvara datetime u format pogodan za <input type="datetime-local">
export function toDatetimeLocal(iso?: string): string {
  const d = iso ? new Date(iso) : new Date();
  if (isNaN(d.getTime())) return "";
  // Korigiraj timezone offset da input prikaze lokalno vrijeme
  const off = d.getTimezoneOffset();
  const local = new Date(d.getTime() - off * 60000);
  return local.toISOString().slice(0, 16);
}

// Pretvara vrijednost iz datetime-local inputa natrag u ISO (s timezone-om).
export function fromDatetimeLocal(value: string): string {
  return new Date(value).toISOString();
}

// Hrvatski nazivi statusa treninga
export const trainingStatusLabel: Record<TrainingStatus, string> = {
  scheduled: "Zakazan",
  in_progress: "U tijeku",
  completed: "Završen",
  cancelled: "Otkazan",
};

export const reservationStatusLabel: Record<ReservationStatus, string> = {
  confirmed: "Potvrđena",
  cancelled: "Otkazana",
};

export const membershipStatusLabel: Record<MembershipStatus, string> = {
  active: "Aktivna",
  cancelled: "Otkazana",
};

export const roleLabel: Record<Role, string> = {
  admin: "Administrator",
  trainer: "Trener",
  member: "Član",
};

// Je li clanarina trenutno aktivna (ista logika kao backend pravilo).
export function isMembershipActive(
  status: MembershipStatus,
  endDate: string,
): boolean {
  if (status !== "active") return false;
  const end = new Date(endDate);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return end >= today;
}
