import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LensMark from "../components/ui/LensMark";

const conditions = [
  {
    name: "Diabetes",
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor"
           strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 3c3.5 4 6 7.4 6 10.5a6 6 0 1 1-12 0C6 10.4 8.5 7 12 3Z" />
      </svg>
    ),
  },
  {
    name: "Cardiovascular",
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor"
           strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M3 12h4l2-5 4 10 2-5h6" />
      </svg>
    ),
  },
];

export default function Landing() {
  const { user } = useAuth();

  return (
    <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-2xl flex-col items-center justify-center px-6 py-20 text-center">
      <div className="glass flex w-full flex-col items-center px-8 py-12 sm:px-14 sm:py-16">
        <span className="flex h-14 w-14 items-center justify-center rounded-full border border-white/60 bg-white/70 text-teal-700 shadow-glass">
          <LensMark className="h-7 w-7" />
        </span>

        <h1 className="mt-7 text-4xl font-semibold leading-tight text-ink sm:text-[2.75rem]">
          Know your risk.
          <br />
          Understand why.
        </h1>

        <p className="mt-5 max-w-md text-[15px] leading-relaxed text-ink/65">
          HealthLens screens for diabetes and cardiovascular risk using
          routine health indicators, then explains exactly which factors are
          driving your result, not just a number.
        </p>

        <div className="mt-6 flex gap-2">
          {conditions.map((c) => (
            <span
              key={c.name}
              className="flex items-center gap-1.5 rounded-full border border-ink/10 bg-white/60 px-3.5 py-1.5 text-xs font-medium text-teal-700"
            >
              {c.icon}
              {c.name}
            </span>
          ))}
        </div>

        <Link to={user ? "/questionnaire" : "/register"} className="btn-primary mt-9 px-7 py-3 text-[15px]">
          {user ? "Start an assessment" : "Get started"}
        </Link>

        <p className="mt-6 text-xs text-ink/50">
          HealthLens is a screening tool, not a medical diagnosis.
        </p>
      </div>
    </main>
  );
}
