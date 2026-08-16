import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../api/client";
import type {
  Student,
  StudentCreate,
  StudentUpdate,
  PaginatedStudents,
  StudentStats,
  StudentFilters,
} from "./types";

const STUDENT_KEYS = {
  all: ["students"] as const,
  lists: () => [...STUDENT_KEYS.all, "list"] as const,
  list: (filters: StudentFilters) => [...STUDENT_KEYS.lists(), filters] as const,
  details: () => [...STUDENT_KEYS.all, "detail"] as const,
  detail: (id: string) => [...STUDENT_KEYS.details(), id] as const,
  stats: () => [...STUDENT_KEYS.all, "stats"] as const,
};

export function useStudents(filters: StudentFilters = {}) {
  return useQuery({
    queryKey: STUDENT_KEYS.list(filters),
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.page) params.append("page", filters.page.toString());
      if (filters.size) params.append("size", filters.size.toString());
      if (filters.search) params.append("search", filters.search);
      if (filters.status) params.append("status", filters.status);
      if (filters.include_deleted) params.append("include_deleted", "true");

      const { data } = await apiClient.get<PaginatedStudents>(
        `/api/students?${params.toString()}`
      );
      return data;
    },
  });
}

export function useStudent(id: string) {
  return useQuery({
    queryKey: STUDENT_KEYS.detail(id),
    queryFn: async () => {
      const { data } = await apiClient.get<Student>(`/api/students/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useStudentStats() {
  return useQuery({
    queryKey: STUDENT_KEYS.stats(),
    queryFn: async () => {
      const { data } = await apiClient.get<StudentStats>("/api/students/stats");
      return data;
    },
  });
}

export function useCreateStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (student: StudentCreate) => {
      const { data } = await apiClient.post<Student>("/api/students", student);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: STUDENT_KEYS.all });
    },
  });
}

export function useUpdateStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: StudentUpdate }) => {
      const { data: updated } = await apiClient.put<Student>(
        `/api/students/${id}`,
        data
      );
      return updated;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: STUDENT_KEYS.all });
      queryClient.invalidateQueries({ queryKey: STUDENT_KEYS.detail(id) });
    },
  });
}

export function useDeleteStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/students/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: STUDENT_KEYS.all });
    },
  });
}
