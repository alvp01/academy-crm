import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStudents, useStudentStats, useDeleteStudent } from "./useStudents";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { SearchBar } from "../../components/ui/SearchBar";
import { StatsCard } from "../dashboard/StatsCard";
import type { StudentStatus } from "./types";

const statusConfig: Record<StudentStatus, { label: string; variant: "success" | "warning" | "error" | "info" | "default" }> = {
  active: { label: "Active", variant: "success" },
  inactive: { label: "Inactive", variant: "default" },
  pending: { label: "Pending", variant: "warning" },
  graduated: { label: "Graduated", variant: "info" },
  deleted: { label: "Deleted", variant: "error" },
};

export function StudentList() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StudentStatus | "">("");
  const [page, setPage] = useState(1);
  const [showDeleted, setShowDeleted] = useState(false);

  const { data: students, isLoading } = useStudents({
    page,
    size: 10,
    search: search || undefined,
    status: statusFilter || undefined,
    include_deleted: showDeleted,
  });

  const { data: stats } = useStudentStats();
  const deleteStudent = useDeleteStudent();

  const handleDelete = (id: string) => {
    if (window.confirm("Are you sure you want to delete this student?")) {
      deleteStudent.mutate(id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text">Students</h1>
          <p className="text-text-light mt-1">Manage your academy's students</p>
        </div>
        <Button onClick={() => navigate("/students/new")}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Student
        </Button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Students"
            value={stats.total.toString()}
            change={`${stats.new_this_month} new this month`}
            changeType="neutral"
            icon={
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            }
          />
          <StatsCard
            title="Active"
            value={stats.active.toString()}
            change={`${Math.round((stats.active / (stats.total || 1)) * 100)}% of total`}
            changeType="positive"
            icon={
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            iconBg="bg-green-100"
          />
          <StatsCard
            title="Pending"
            value={stats.pending.toString()}
            change="Awaiting payment"
            changeType="neutral"
            icon={
              <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            iconBg="bg-amber-100"
          />
          <StatsCard
            title="Graduated"
            value={stats.graduated.toString()}
            change="Completed courses"
            changeType="positive"
            icon={
              <svg className="w-6 h-6 text-brand-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
              </svg>
            }
            iconBg="bg-brand-100"
          />
        </div>
      )}

      {/* Filters and search */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <SearchBar
              placeholder="Search by name, email, phone, or ID..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as StudentStatus | "");
                setPage(1);
              }}
              className="px-4 py-2 border border-surface-border rounded-xl text-text bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="pending">Pending</option>
              <option value="graduated">Graduated</option>
            </select>
            <label className="flex items-center gap-2 px-4 py-2 border border-surface-border rounded-xl bg-white cursor-pointer">
              <input
                type="checkbox"
                checked={showDeleted}
                onChange={(e) => {
                  setShowDeleted(e.target.checked);
                  setPage(1);
                }}
                className="w-4 h-4 rounded border-surface-border text-brand-700 focus:ring-brand-500"
              />
              <span className="text-sm text-text-light whitespace-nowrap">Show deleted</span>
            </label>
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card className="p-0">
        {isLoading ? (
          <div className="p-8 text-center text-text-light">Loading...</div>
        ) : !students?.items.length ? (
          <div className="p-8 text-center text-text-light">No students found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="text-left px-6 py-4 font-medium text-text-light">Name</th>
                  <th className="text-left px-6 py-4 font-medium text-text-light hidden sm:table-cell">Email</th>
                  <th className="text-left px-6 py-4 font-medium text-text-light hidden md:table-cell">Phone</th>
                  <th className="text-center px-6 py-4 font-medium text-text-light">Status</th>
                  <th className="text-right px-6 py-4 font-medium text-text-light">Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.items.map((student) => (
                  <tr
                    key={student.id}
                    className="border-b border-surface-border last:border-0 hover:bg-surface-background transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 gradient-brand rounded-full flex items-center justify-center text-white font-medium text-sm">
                          {student.first_name[0]}{student.last_name[0]}
                        </div>
                        <div>
                          <p className="font-medium text-text">
                            {student.first_name} {student.last_name}
                          </p>
                          <p className="text-sm text-text-light sm:hidden">{student.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-text-light hidden sm:table-cell">{student.email}</td>
                    <td className="px-6 py-4 text-text-light hidden md:table-cell">{student.phone_number}</td>
                    <td className="px-6 py-4 text-center">
                      <Badge variant={statusConfig[student.status]?.variant || "default"}>
                        {statusConfig[student.status]?.label || student.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => navigate(`/students/${student.id}`)}
                          className="p-2 hover:bg-brand-50 rounded-lg transition-colors text-text-light hover:text-brand-700"
                          title="View"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => navigate(`/students/${student.id}/edit`)}
                          className="p-2 hover:bg-brand-50 rounded-lg transition-colors text-text-light hover:text-brand-700"
                          title="Edit"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(student.id)}
                          className="p-2 hover:bg-red-50 rounded-lg transition-colors text-text-light hover:text-red-600"
                          title="Delete"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {students && students.total > 10 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-surface-border">
            <p className="text-sm text-text-light">
              Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, students.total)} of {students.total} students
            </p>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 10 >= students.total}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
