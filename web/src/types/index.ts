// Tipovi koji 1:1 odgovaraju Pydantic shemama na backendu.
// Ako se backend promijeni, ovdje se mijenja.

export type Role = "admin" | "trainer" | "member";

// Odgovara UserResponse (schemas/user.py)
export interface User {
  id: number;
  username: string;
  role: Role;
  is_active: boolean;
}

// Odgovara TokenResponse (schemas/auth.py)
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Odgovara TrainerInfo (ugnijezdeno u TrainingResponse)
export interface TrainerInfo {
  id: number;
  username: string;
}

export type TrainingStatus =
  | "scheduled"
  | "in_progress"
  | "completed"
  | "cancelled";

// Odgovara TrainingResponse (schemas/training.py)
export interface Training {
  id: number;
  title: string;
  scheduled_at: string; // ISO datetime string
  duration_minutes: number;
  max_capacity: number;
  status: TrainingStatus;
  trainer: TrainerInfo | null;
}

// Tijelo za kreiranje treninga (TrainingCreate)
export interface TrainingCreatePayload {
  title: string;
  scheduled_at: string;
  duration_minutes: number;
  max_capacity: number;
}

// Tijelo za izmjenu treninga (TrainingUpdate) - sva polja opcionalna
export interface TrainingUpdatePayload {
  title?: string;
  scheduled_at?: string;
  duration_minutes?: number;
  max_capacity?: number;
}

export type ReservationStatus = "confirmed" | "cancelled";

// Odgovara ReservationResponse (schemas/reservation.py)
export interface Reservation {
  id: number;
  training_id: number;
  status: ReservationStatus;
  user: User | null;
}

export type MembershipStatus = "active" | "cancelled";

// Odgovara MembershipResponse (schemas/membership.py)
export interface Membership {
  id: number;
  user_id: number;
  start_date: string; // ISO date string (YYYY-MM-DD)
  end_date: string;
  status: MembershipStatus;
}

// Tijelo za kreiranje clanarine (MembershipCreate)
export interface MembershipCreatePayload {
  user_id: number;
  start_date: string;
  end_date: string;
}

// Format greske s backenda (core/errors.py -> AppError)
export interface ApiError {
  code: string;
  message: string;
}
