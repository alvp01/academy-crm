# Frontend Component Creation Guideline

This document establishes the conventions for creating, organizing, and maintaining reusable React components in the Academy CRM frontend.

---

## 1. Screaming Architecture

The directory structure should **scream what the application does**, not how it's built.

### Directory Structure

```
src/
├── components/
│   ├── ui/                    # Atomic, domain-agnostic UI primitives
│   └── layout/                # Structural layout components
├── features/
│   ├── auth/                  # Authentication domain
│   ├── dashboard/             # Dashboard domain
│   ├── students/              # Students domain (future)
│   ├── courses/               # Courses domain (future)
│   ├── schedule/              # Schedule domain (future)
│   └── payments/              # Payments domain (future)
├── hooks/                     # Shared custom hooks
├── store/                     # Zustand stores
├── api/                       # API client and endpoints
└── types/                     # Shared TypeScript types
```

### Rules

1. **Feature folders represent business domains** — `auth/`, `dashboard/`, `students/`, `courses/`
2. **Never organize by type** — No `components/`, `utils/`, `helpers/` at the root
3. **Each feature is self-contained** — Pages, components, hooks, and types live together
4. **Shared code goes up** — If a component is used across 3+ features, move it to `components/ui/`

---

## 2. Atomic UI Components (`components/ui/`)

These are **pure, domain-agnostic primitives**. They know nothing about students, courses, or payments.

### Characteristics

- **No business logic** — Only presentation and user interaction
- **Fully composable** — Accept `children`, `className`, and variant props
- **Accessible** — Use semantic HTML, ARIA attributes where needed
- **Type-safe** — Extend native HTML element props via `React.ComponentProps`

### Component Template

```tsx
import { ReactNode } from "react";

interface MyComponentProps {
  variant?: "primary" | "secondary";
  children: ReactNode;
  className?: string;
}

const variantClasses = {
  primary: "bg-brand-700 text-white",
  secondary: "border border-brand-700 text-brand-700",
};

export function MyComponent({
  variant = "primary",
  children,
  className = "",
}: MyComponentProps) {
  return (
    <div className={`base-classes ${variantClasses[variant]} ${className}`}>
      {children}
    </div>
  );
}
```

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Props over props** | Use discriminated unions for variants, not boolean flags |
| **className passthrough** | Always accept `className` for composition |
| **Default exports** | One component per file, named export |
| **Barrel exports** | Re-export from `index.ts` for clean imports |
| **No side effects** | Pure functions, no API calls, no state mutations |

### Existing Components

| Component | Purpose | Props |
|-----------|---------|-------|
| `Button` | Action trigger | `variant`, `size`, `disabled`, `children` |
| `Input` | Text input | `label`, `error`, `type`, `placeholder` |
| `Card` | Content container | `elevated`, `children`, `className` |
| `Badge` | Status indicator | `variant`, `children` |
| `Avatar` | User representation | `name`, `src`, `size` |
| `Alert` | Feedback message | `variant`, `children` |
| `SearchBar` | Search input | `placeholder`, `value`, `onChange` |
| `ToggleGroup` | Segmented control | `value`, `onChange`, `options` |

---

## 3. Layout Components (`components/layout/`)

Structural components that define **page-level composition patterns**.

### Characteristics

- **Define spatial relationships** — Sidebar + content, header + body
- **Handle responsive behavior** — Mobile hamburger, desktop sidebar
- **Manage navigation state** — Active routes, expanded sections

### Existing Layouts

| Layout | Structure | Use Case |
|--------|-----------|----------|
| `AuthLayout` | Split-screen (brand + form) | Login, Register |
| `DashboardLayout` | Sidebar + topbar + content | Main app |
| `Sidebar` | Fixed navigation | Dashboard pages |
| `Topbar` | Sticky header | Dashboard pages |

### Composition Pattern

```tsx
// DashboardWrapper.tsx - Composes layout from primitives
function DashboardWrapper() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <DashboardLayout
      sidebar={<Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />}
      topbar={<Topbar onMenuClick={() => setSidebarOpen(true)} />}
    />
  );
}
```

---

## 4. Feature Components (`features/`)

Domain-specific components that implement business logic and compose UI primitives.

### Feature Folder Structure

```
features/
└── students/
    ├── StudentList.tsx           # Page component
    ├── StudentCard.tsx           # Reusable domain component
    ├── StudentForm.tsx           # Form component
    ├── useStudents.ts            # Custom hook for data fetching
    ├── types.ts                  # Domain-specific types
    └── index.ts                  # Barrel export
```

### Component Hierarchy

```
Page Component (feature/FeaturePage.tsx)
├── Domain Components (feature/DomainComponent.tsx)
│   └── UI Primitives (components/ui/*.tsx)
└── Custom Hooks (feature/useFeature.ts)
    └── API Layer (api/client.ts)
```

### Naming Conventions

| Level | Naming | Example |
|-------|--------|---------|
| Page | `{Domain}Page` | `DashboardPage`, `StudentListPage` |
| Domain | `{Entity}{Component}` | `StudentCard`, `CourseTable` |
| UI Primitive | `{Concept}` | `Button`, `Input`, `Card` |
| Hook | `use{Domain}` | `useStudents`, `useAuth` |

---

## 5. Composition Patterns

### Pattern 1: Variant-Based Composition

Use discriminated unions for visual variants:

```tsx
interface ButtonProps {
  variant: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

const variantClasses = {
  primary: "bg-brand-700 text-white hover:bg-brand-800",
  secondary: "border-2 border-brand-700 text-brand-700",
  ghost: "text-brand-700 hover:bg-brand-50",
  danger: "bg-red-500 text-white hover:bg-red-600",
};
```

### Pattern 2: Compound Components

Group related components under a namespace:

```tsx
import { Card, CardHeader, CardTitle } from "@/components/ui";

<Card>
  <CardHeader>
    <CardTitle>Recent Enrollments</CardTitle>
  </CardHeader>
  {/* content */}
</Card>
```

### Pattern 3: Render Props for Customization

Pass render functions for maximum flexibility:

```tsx
interface StatsCardProps {
  icon: ReactNode;
  iconBg?: string;
}

<StatsCard
  icon={<svg>...</svg>}
  iconBg="bg-brand-100"
/>
```

### Pattern 4: Layout Injection

Pass layout components as props:

```tsx
interface DashboardLayoutProps {
  sidebar: ReactNode;
  topbar: ReactNode;
}

<DashboardLayout
  sidebar={<Sidebar />}
  topbar={<Topbar />}
/>
```

---

## 6. File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Component | `PascalCase.tsx` | `Button.tsx`, `StudentCard.tsx` |
| Hook | `camelCase.ts` | `useStudents.ts` |
| Type | `camelCase.ts` | `types.ts` |
| Utility | `camelCase.ts` | `formatCurrency.ts` |
| Barrel | `index.ts` | `index.ts` |

---

## 7. Import Conventions

Use the `@/` path alias for absolute imports:

```tsx
// ✅ Good - Absolute imports
import { Button } from "@/components/ui";
import { useAuth } from "@/store/auth";
import { apiClient } from "@/api/client";

// ❌ Bad - Relative imports
import { Button } from "../../components/ui/Button";
import { useAuth } from "../store/auth";
```

---

## 8. Responsive Design Rules

### Breakpoint Strategy (Mobile-First)

```tsx
// Base: Mobile (default)
// sm: 640px - Large phones
// md: 768px - Tablets
// lg: 1024px - Desktop
// xl: 1280px - Large desktop

<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
```

### Mobile Patterns

| Pattern | Implementation |
|---------|----------------|
| Sidebar | Hidden by default, hamburger toggle, overlay |
| Topbar | Hamburger menu button visible on `lg:hidden` |
| Cards | Stack vertically on mobile |
| Forms | Full-width inputs, stacked layout |

---

## 9. Adding a New Feature

### Step-by-Step

1. **Create feature folder** — `src/features/{domain}/`
2. **Define types** — `types.ts` with interfaces
3. **Create custom hook** — `use{Domain}.ts` for data fetching
4. **Build domain components** — Compose UI primitives
5. **Create page component** — `{Domain}Page.tsx`
6. **Add barrel export** — `index.ts`
7. **Register routes** — Add to `App.tsx`

### Example: Adding Students Feature

```tsx
// features/students/types.ts
export interface Student {
  id: string;
  name: string;
  email: string;
  enrolledAt: Date;
}

// features/students/useStudents.ts
export function useStudents() {
  // Data fetching logic
}

// features/students/StudentCard.tsx
import { Card, Avatar, Badge } from "@/components/ui";

export function StudentCard({ student }: { student: Student }) {
  return (
    <Card>
      <Avatar name={student.name} />
      <p>{student.name}</p>
      <Badge variant="success">Active</Badge>
    </Card>
  );
}

// features/students/StudentListPage.tsx
export function StudentListPage() {
  return (
    <div>
      <h1>Students</h1>
      {/* Student cards grid */}
    </div>
  );
}

// features/students/index.ts
export { StudentListPage } from "./StudentListPage";
```

---

## 10. Checklist: Creating a New Component

- [ ] **Is it domain-agnostic?** → `components/ui/`
- [ ] **Is it domain-specific?** → `features/{domain}/`
- [ ] **Does it accept `className`?** → For composition
- [ ] **Does it use variant props?** → Discriminated unions, not booleans
- [ ] **Is it fully typed?** → Extend native props where applicable
- [ ] **Does it have a barrel export?** → `index.ts`
- [ ] **Is it responsive?** → Mobile-first with `sm:`/`md:`/`lg:` breakpoints
- [ ] **Is it accessible?** → Semantic HTML, ARIA, keyboard navigation
- [ ] **Does it handle loading/error states?** → If data-dependent
- [ ] **Is it documented?** → JSDoc for complex props

---

## 11. Anti-Patterns to Avoid

| Anti-Pattern | Why | Fix |
|--------------|-----|-----|
| Organizing by file type | Screams "how", not "what" | Use feature folders |
| Boolean prop explosion | `isPrimary`, `isSecondary`, `isDanger` | Use variant union |
| Prop drilling 3+ levels | Tight coupling, hard to refactor | Use composition or context |
| Large components (>200 lines) | Hard to understand and test | Split into smaller components |
| Inline styles | Hard to override, no design tokens | Use Tailwind classes |
| Relative imports | Fragile paths, hard to refactor | Use `@/` alias |

---

## 12. Design Token Reference

| Token | Value | Usage |
|-------|-------|-------|
| `brand-700` | `#6E39CB` | Primary actions, links |
| `brand-500` | `#9154FD` | Hover states, gradients |
| `brand-100` | `#E7E7F4` | Light backgrounds |
| `surface-background` | `#F4F5F9` | Page background |
| `text` | `#3A3541` | Primary text |
| `text-light` | `#89868D` | Secondary text |

---

*Last updated: August 2026*
