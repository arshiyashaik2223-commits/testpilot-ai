import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const onDashboard = location.pathname === "/";

  return (
    <aside className="w-60 shrink-0 border-r border-border bg-surface flex flex-col justify-between">
      <div>
        <div className="px-6 py-6 border-b border-border">
          <Link to="/" className="text-lg font-semibold tracking-tight text-textPrimary">
            TestPilot <span className="text-accent">AI</span>
          </Link>
        </div>

        <nav className="px-3 py-4">
          <Link
            to="/"
            className={`block rounded px-3 py-2 text-sm mb-1 transition-colors ${
              onDashboard
                ? "bg-surfaceRaised text-textPrimary"
                : "text-textMuted hover:text-textPrimary hover:bg-surfaceRaised"
            }`}
          >
            Projects
          </Link>
        </nav>
      </div>

      <div className="px-6 py-5 border-t border-border">
        <p className="text-sm text-textPrimary truncate">{user?.name}</p>
        <p className="text-xs text-textMuted truncate mb-3">{user?.email}</p>
        <button
          onClick={logout}
          className="text-xs text-textMuted hover:text-fail transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
