import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Landing() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-2xl px-6 py-20 text-center">
      <h1 className="mb-4 text-4xl text-teal-900">
        Know your risk. Understand why.
      </h1>
      <p className="mb-10 text-teal-700">
        HealthLens screens for diabetes and cardiovascular risk using
        routine health indicators, then explains exactly which factors are
        driving your result — not just a number.
      </p>
      <Link
        to={user ? "/questionnaire" : "/register"}
        className="rounded-md bg-teal-600 px-6 py-3 font-medium text-white hover:bg-teal-700"
      >
        {user ? "Start an assessment" : "Get started"}
      </Link>
      <p className="mt-6 text-xs text-teal-700">
        HealthLens is a screening tool, not a medical diagnosis.
      </p>
    </div>
  );
}
