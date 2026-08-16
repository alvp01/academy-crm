import { Link } from "react-router-dom";
import { AuthLayout } from "../../components/layout/AuthLayout";
import { RegisterForm } from "./RegisterForm";

const features = [
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    ),
    title: "Create your account",
    description: "Get started with your academy management",
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    title: "Quick setup",
    description: "Get your academy running in minutes, not days",
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    title: "Secure & reliable",
    description: "Your data is encrypted and backed up automatically",
  },
];

export function RegisterPage() {
  return (
    <AuthLayout
      title="Join thousands of academies"
      subtitle="Sign Up"
      features={features}
    >
      <RegisterForm />
      <p className="text-center mt-8 text-text-light">
        Already have an account?{" "}
        <Link to="/login" className="text-brand-700 font-medium hover:text-brand-800">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
