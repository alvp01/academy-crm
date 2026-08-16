export type StudentStatus = "active" | "inactive" | "pending" | "graduated" | "deleted";

export interface Student {
  id: string;
  academy_id: string;
  first_name: string;
  last_name: string;
  email: string;
  identification_number: string;
  phone_number: string;
  address: string;
  date_of_birth: string;
  allergies: string;
  referral_source: string;
  occupation: string;
  status: StudentStatus;
  created_at: string;
  updated_at: string;
}

export interface StudentCreate {
  first_name: string;
  last_name: string;
  email: string;
  identification_number: string;
  phone_number: string;
  address: string;
  date_of_birth: string;
  allergies?: string;
  referral_source: string;
  occupation: string;
}

export interface StudentUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  identification_number?: string;
  phone_number?: string;
  address?: string;
  date_of_birth?: string;
  allergies?: string;
  referral_source?: string;
  occupation?: string;
  status?: StudentStatus;
}

export interface PaginatedStudents {
  items: Student[];
  total: number;
  page: number;
  size: number;
}

export interface StudentStats {
  total: number;
  active: number;
  inactive: number;
  pending: number;
  graduated: number;
  new_this_month: number;
}

export interface StudentFilters {
  page?: number;
  size?: number;
  search?: string;
  status?: StudentStatus;
  include_deleted?: boolean;
}
