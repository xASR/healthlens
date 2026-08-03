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
    <header className="border-b border-teal-100 bg-sand-50">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link to="/" className="font-display text-xl font-semibold text-teal-900">
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
              className="rounded-md border border-teal-600 px-3 py-1.5 text-teal-700 hover:bg-teal-50"
            >
              Log out
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}
