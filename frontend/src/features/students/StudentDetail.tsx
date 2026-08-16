import { useParams, useNavigate } from "react-router-dom";
import { useStudent, useDeleteStudent } from "./useStudents";
import { Card, CardHeader, CardTitle } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";

const statusConfig = {
  active: { label: "Active", variant: "success" as const },
  inactive: { label: "Inactive", variant: "default" as const },
  pending: { label: "Pending", variant: "warning" as const },
  graduated: { label: "Graduated", variant: "info" as const },
  deleted: { label: "Deleted", variant: "error" as const },
};

export function StudentDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: student, isLoading } = useStudent(id || "");
  const deleteStudent = useDeleteStudent();

  if (isLoading) {
    return <div className="text-center py-8 text-text-light">Loading...</div>;
  }

  if (!student) {
    return <div className="text-center py-8 text-text-light">Student not found</div>;
  }

  const handleDelete = () => {
    if (window.confirm("Are you sure you want to delete this student?")) {
      deleteStudent.mutate(student.id, {
        onSuccess: () => navigate("/students"),
      });
    }
  };

  const status = statusConfig[student.status] || statusConfig.active;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/students")}
            className="p-2 hover:bg-brand-50 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 gradient-brand rounded-full flex items-center justify-center text-white font-bold text-xl">
              {student.first_name[0]}{student.last_name[0]}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-text">
                {student.first_name} {student.last_name}
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant={status.variant}>{status.label}</Badge>
                <span className="text-sm text-text-light">
                  Joined {new Date(student.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => navigate(`/students/${student.id}/edit`)}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Full Name</span>
              <span className="font-medium text-text">{student.first_name} {student.last_name}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Email</span>
              <span className="font-medium text-text">{student.email}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Phone</span>
              <span className="font-medium text-text">{student.phone_number}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Date of Birth</span>
              <span className="font-medium text-text">
                {new Date(student.date_of_birth).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Address</span>
              <span className="font-medium text-text text-right max-w-[60%]">{student.address}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-text-light">Occupation</span>
              <span className="font-medium text-text">{student.occupation}</span>
            </div>
          </div>
        </Card>

        {/* Additional Details */}
        <Card>
          <CardHeader>
            <CardTitle>Additional Details</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">ID Number</span>
              <span className="font-medium text-text font-mono">{student.identification_number}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Referral Source</span>
              <span className="font-medium text-text">{student.referral_source}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Allergies</span>
              <span className="font-medium text-text">{student.allergies}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-surface-border">
              <span className="text-text-light">Status</span>
              <Badge variant={status.variant}>{status.label}</Badge>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-text-light">Last Updated</span>
              <span className="font-medium text-text">
                {new Date(student.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Enrolled Classes placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Enrolled Classes</CardTitle>
        </CardHeader>
        <div className="text-center py-8 text-text-light">
          <svg className="w-12 h-12 mx-auto mb-4 text-text-light/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <p>Class enrollment coming soon</p>
        </div>
      </Card>
    </div>
  );
}
