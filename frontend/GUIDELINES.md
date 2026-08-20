# Frontend Coding Guidelines

This document establishes conventions for the React/TypeScript frontend.

For component-specific patterns, see also: [COMPONENT-GUIDELINES.md](./COMPONENT-GUIDELINES.md)

---

## 1. Screaming Architecture

The directory structure should **scream what the application does**, not how it's built.

### Directory Structure

```
src/
├── api/                       # API client and endpoint definitions
├── components/
│   ├── ui/                    # Atomic, domain-agnostic UI primitives
│   └── layout/                # Structural layout components
├── features/
│   ├── auth/                  # Authentication domain
│   ├── dashboard/             # Dashboard domain
│   ├── students/              # Students domain
│   └── ...                    # Other business domains
├── store/                     # Zustand stores (client state)
├── App.tsx                    # Route definitions
├── main.tsx                   # Entry point
└── index.css                  # Global styles + Tailwind
```

### Rules

1. **Feature folders represent business domains** — `auth/`, `dashboard/`, `students/`
2. **Never organize by type** — No root-level `components/`, `utils/`, `helpers/`
3. **Each feature is self-contained** — Pages, components, hooks, types live together
4. **Shared code goes up** — Used across 3+ features → `components/ui/`

---

## 2. State Management

### Server State: TanStack Query

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

// Query
export function useStudents(academyId: string) {
  return useQuery({
    queryKey: ["students", academyId],
    queryFn: () => apiClient.get(`/api/students?academy_id=${academyId}`),
  });
}

// Mutation
export function useCreateStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateStudentInput) =>
      apiClient.post("/api/students", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students"] });
    },
  });
}
```

### Client State: Zustand

```typescript
import { create } from "zustand";

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
```

### Rules

| Data Type | Store | Example |
|-----------|-------|---------|
| Server data (API responses) | TanStack Query | Students list, classroom details |
| UI state (non-persisted) | Zustand | Sidebar open, modal state |
| Form state | React Hook Form | Form inputs, validation |
| Auth tokens | HttpOnly cookies | Access/refresh tokens |

---

## 3. Component Patterns

### Base Component Template

```tsx
import { ReactNode } from "react";

interface ButtonProps {
  variant: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

const variantClasses = {
  primary: "bg-brand-700 text-white hover:bg-brand-800",
  secondary: "border-2 border-brand-700 text-brand-700 hover:bg-brand-50",
  ghost: "text-brand-700 hover:bg-brand-50",
  danger: "bg-red-500 text-white hover:bg-red-600",
};

const sizeClasses = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-base",
  lg: "px-6 py-3 text-lg",
};

export function Button({
  variant,
  size = "md",
  disabled = false,
  children,
  className = "",
  onClick,
}: ButtonProps) {
  return (
    <button
      className={`rounded-lg font-medium transition-colors ${variantClasses[variant]} ${sizeClasses[size]} ${disabled ? "opacity-50 cursor-not-allowed" : ""} ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### Patterns

| Pattern | When | Example |
|---------|------|---------|
| **Variant-based** | Visual alternatives | Button variants, alert types |
| **Compound** | Related sub-components | Card + CardHeader + CardTitle |
| **Render props** | Customization slots | Icon rendering |
| **Layout injection** | Page composition | Sidebar + content |

---

## 4. Custom Hooks

### Data Fetching Hook

```typescript
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

interface Student {
  id: string;
  name: string;
  email: string;
}

export function useStudents() {
  return useQuery<Student[]>({
    queryKey: ["students"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/students");
      return data.items;
    },
  });
}
```

### Mutation Hook

```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

export function useDeleteStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/students/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students"] });
    },
  });
}
```

### Naming Convention

```typescript
// ✅ Correct
useStudents()           // List of students
useStudent(id)          // Single student
useCreateStudent()      // Create mutation
useUpdateStudent()      // Update mutation
useDeleteStudent()      // Delete mutation

// ❌ Wrong
getStudents()           // Missing "use" prefix
fetchStudentList()      // Not idiomatic
```

---

## 5. Forms

### Pattern with React Hook Form

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Input, Button } from "@/components/ui";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
});

type FormData = z.infer<typeof schema>;

export function StudentForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    // API call
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input
        label="Name"
        {...register("name")}
        error={errors.name?.message}
      />
      <Input
        label="Email"
        type="email"
        {...register("email")}
        error={errors.email?.message}
      />
      <Button type="submit" disabled={isSubmitting}>
        Save
      </Button>
    </form>
  );
}
```

### Rules

- Define validation schema with Zod
- Use `zodResolver` for integration
- Show errors inline on each field
- Disable submit button while submitting
- Reset form on success

---

## 6. API Client

### Setup

```typescript
// src/api/client.ts
import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8001",
  withCredentials: true, // Send cookies
});

// Request interceptor for CSRF
apiClient.interceptors.request.use((config) => {
  if (config.method !== "get") {
    const csrfToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrf_token="))
      ?.split("=")[1];

    if (csrfToken) {
      config.headers["X-CSRF-Token"] = csrfToken;
    }
  }
  return config;
});

// Response interceptor for 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
```

### Endpoint Definitions

```typescript
// src/api/endpoints.ts
export const endpoints = {
  auth: {
    login: "/api/auth/login",
    register: "/api/auth/register",
    refresh: "/api/auth/refresh",
    logout: "/api/auth/logout",
  },
  students: {
    list: "/api/students",
    get: (id: string) => `/api/students/${id}`,
    create: "/api/students",
    update: (id: string) => `/api/students/${id}`,
    delete: (id: string) => `/api/students/${id}`,
  },
  // ... other endpoints
} as const;
```

---

## 7. Import Conventions

### Use `@/` Alias

```tsx
// ✅ Correct - Absolute imports
import { Button } from "@/components/ui";
import { useStudents } from "@/features/students/useStudents";
import { apiClient } from "@/api/client";
import { useAuthStore } from "@/store/auth";

// ❌ Wrong - Relative imports
import { Button } from "../../components/ui/Button";
import { useStudents } from "../features/students/useStudents";
```

### Import Order

```tsx
// 1. React / third-party
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

// 2. Shared UI components
import { Button, Card, Input } from "@/components/ui";

// 3. Feature imports
import { useStudents } from "@/features/students/useStudents";

// 4. API / store
import { apiClient } from "@/api/client";
import { useAuthStore } from "@/store/auth";

// 5. Types
import type { Student } from "@/features/students/types";
```

---

## 8. Routing

### Pattern

```tsx
// src/App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { DashboardLayout } from "@/components/layout/DashboardLayout";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/students" element={<StudentsPage />} />
            <Route path="/classrooms" element={<ClassroomsPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 9. Error Handling

### API Errors

```typescript
// In hooks
const { data, error, isLoading } = useQuery({
  queryKey: ["students"],
  queryFn: fetchStudents,
});

if (error) {
  // Handle error - show toast, fallback UI, etc.
  toast.error("Failed to load students");
}
```

### Component Errors

```tsx
import { Alert } from "@/components/ui";

export function StudentList({ students, error }: Props) {
  if (error) {
    return <Alert variant="error">Failed to load students</Alert>;
  }

  if (students.length === 0) {
    return <EmptyState message="No students found" />;
  }

  return (
    <div>
      {students.map((student) => (
        <StudentCard key={student.id} student={student} />
      ))}
    </div>
  );
}
```

---

## 10. Testing Patterns

### Component Testing

```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "./Button";

describe("Button", () => {
  it("renders with correct text", () => {
    render(<Button variant="primary">Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<Button variant="primary" onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText("Click"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Hook Testing

```tsx
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useStudents } from "./useStudents";

const createWrapper = () => {
  const queryClient = new QueryClient();
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe("useStudents", () => {
  it("fetches students", async () => {
    const { result } = renderHook(() => useStudents(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
```

---

## 11. Code Style

### Formatting

- **Semicolons**: No semicolons
- **Quotes**: Double quotes
- **Trailing commas**: Always
- **Line length**: 80 characters (soft limit)

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Components | `PascalCase.tsx` | `StudentCard.tsx` |
| Hooks | `use{Domain}.ts` | `useStudents.ts` |
| Types | `types.ts` | `types.ts` |
| Utilities | `camelCase.ts` | `formatDate.ts` |
| Constants | `UPPER_SNAKE_CASE` | `API_BASE_URL` |

---

## 12. Checklist for New Features

- [ ] Feature folder created: `src/features/{domain}/`
- [ ] Types defined: `types.ts`
- [ ] API hooks created: `use{Domain}.ts`
- [ ] Domain components built (compose UI primitives)
- [ ] Page component created: `{Domain}Page.tsx`
- [ ] Barrel export added: `index.ts`
- [ ] Route registered in `App.tsx`
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Empty states handled

---

*Last updated: August 2026*
