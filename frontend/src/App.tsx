import { useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DashboardLayout } from "./components/layout/DashboardLayout";
import { Sidebar } from "./components/layout/Sidebar";
import { Topbar } from "./components/layout/Topbar";
import { LoginPage, RegisterPage } from "./features/auth";
import { DashboardPage } from "./features/dashboard";
import { StudentList, StudentDetail, StudentForm } from "./features/students";

function DashboardWrapper() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <DashboardLayout
      sidebar={<Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />}
      topbar={<Topbar onMenuClick={() => setSidebarOpen(true)} />}
    />
  );
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          element={
            <ProtectedRoute>
              <DashboardWrapper />
            </ProtectedRoute>
          }
        >
          <Route path="/protected" element={<DashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/students" element={<StudentList />} />
          <Route path="/students/new" element={<StudentForm />} />
          <Route path="/students/:id" element={<StudentDetail />} />
          <Route path="/students/:id/edit" element={<StudentForm />} />
        </Route>
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}
