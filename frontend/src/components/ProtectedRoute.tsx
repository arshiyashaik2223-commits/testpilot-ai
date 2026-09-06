import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Sidebar from "./Sidebar";

export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-base">
      <Sidebar />
      <main className="flex-1 px-8 py-8 max-w-5xl">
        <Outlet />
      </main>
    </div>
  );
}
