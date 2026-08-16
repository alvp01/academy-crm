import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useStudent, useCreateStudent, useUpdateStudent } from "./useStudents";
import { Card, CardHeader, CardTitle } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Alert } from "../../components/ui/Alert";
import { useForm } from "react-hook-form";
import type { StudentCreate, StudentUpdate } from "./types";

interface StudentFormData {
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
}

export function StudentForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = !!id;

  const { data: existingStudent, isLoading: isLoadingStudent } = useStudent(id || "");
  const createStudent = useCreateStudent();
  const updateStudent = useUpdateStudent();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<StudentFormData>();

  useEffect(() => {
    if (existingStudent) {
      reset({
        first_name: existingStudent.first_name,
        last_name: existingStudent.last_name,
        email: existingStudent.email,
        identification_number: existingStudent.identification_number,
        phone_number: existingStudent.phone_number,
        address: existingStudent.address,
        date_of_birth: existingStudent.date_of_birth.split("T")[0],
        allergies: existingStudent.allergies,
        referral_source: existingStudent.referral_source,
        occupation: existingStudent.occupation,
      });
    }
  }, [existingStudent, reset]);

  const onSubmit = async (data: StudentFormData) => {
    try {
      if (isEditing && id) {
        await updateStudent.mutateAsync({ id, data: data as StudentUpdate });
        navigate(`/students/${id}`);
      } else {
        const newStudent = await createStudent.mutateAsync(data as StudentCreate);
        navigate(`/students/${newStudent.id}`);
      }
    } catch (error) {
      // Error is handled by the mutation
    }
  };

  if (isEditing && isLoadingStudent) {
    return <div className="text-center py-8 text-text-light">Loading...</div>;
  }

  const error = createStudent.error || updateStudent.error;
  const errorMessage = error instanceof Error ? error.message : null;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(isEditing ? `/students/${id}` : "/students")}
          className="p-2 hover:bg-brand-50 rounded-lg transition-colors"
        >
          <svg className="w-5 h-5 text-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 className="text-2xl font-bold text-text">
          {isEditing ? "Edit Student" : "New Student"}
        </h1>
      </div>

      {errorMessage && (
        <Alert variant="error">{errorMessage}</Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="First Name"
                {...register("first_name", { required: "First name is required" })}
                error={errors.first_name?.message}
                placeholder="Enter first name"
              />
              <Input
                label="Last Name"
                {...register("last_name", { required: "Last name is required" })}
                error={errors.last_name?.message}
                placeholder="Enter last name"
              />
            </div>
            <Input
              label="Email"
              type="email"
              {...register("email", {
                required: "Email is required",
                pattern: { value: /^\S+@\S+\.\S+$/, message: "Invalid email" },
              })}
              error={errors.email?.message}
              placeholder="student@email.com"
            />
            <Input
              label="Phone Number"
              type="tel"
              {...register("phone_number", { required: "Phone number is required" })}
              error={errors.phone_number?.message}
              placeholder="+1 234 567 890"
            />
            <Input
              label="Date of Birth"
              type="date"
              {...register("date_of_birth", { required: "Date of birth is required" })}
              error={errors.date_of_birth?.message}
            />
            <Input
              label="Address"
              {...register("address", { required: "Address is required" })}
              error={errors.address?.message}
              placeholder="Enter full address"
            />
          </div>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Additional Information</CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <Input
              label="ID Number"
              {...register("identification_number", { required: "ID number is required" })}
              error={errors.identification_number?.message}
              placeholder="Enter identification number"
            />
            <Input
              label="Occupation"
              {...register("occupation", { required: "Occupation is required" })}
              error={errors.occupation?.message}
              placeholder="Enter occupation"
            />
            <Input
              label="Referral Source"
              {...register("referral_source", { required: "Referral source is required" })}
              error={errors.referral_source?.message}
              placeholder="How did they find us?"
            />
            <Input
              label="Allergies"
              {...register("allergies")}
              placeholder="Known allergies (default: N/A)"
            />
          </div>
        </Card>

        <div className="flex justify-end gap-4 mt-6">
          <Button
            type="button"
            variant="ghost"
            onClick={() => navigate(isEditing ? `/students/${id}` : "/students")}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={createStudent.isPending || updateStudent.isPending}
          >
            {createStudent.isPending || updateStudent.isPending
              ? "Saving..."
              : isEditing
              ? "Save Changes"
              : "Create Student"}
          </Button>
        </div>
      </form>
    </div>
  );
}
