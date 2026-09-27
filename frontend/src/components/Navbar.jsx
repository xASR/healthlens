import { Link, useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { auth } from "../firebase";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await signOut(auth);
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-40 border-b border-white/50 bg-white/60 backdrop-blur-xl backdrop-saturate-150">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link to="/" className="font-display text-xl font-semibold tracking-tight text-teal-900">
          HealthLens
        </Link>
        {user && (
          <nav className="flex items-center gap-6 text-sm font-medium text-teal-700">
            <Link to="/questionnaire" className="hover:text-teal-900">
              New Assessment
            </Link>
            <Link to="/dashboard" className="hover:text-teal-900">
              Dashboard
            </Link>
            <button
              onClick={handleLogout}
              className="rounded-full border border-ink/10 bg-white/70 px-4 py-1.5 text-teal-700 transition hover:bg-white"
            >
              Log out
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}
