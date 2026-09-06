import { createContext, useContext, useState, ReactNode } from "react";
import { apiClient, apiErrorMessage } from "../api/client";
import { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function readStoredUser(): User | null {
  const raw = localStorage.getItem("testpilot_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(readStoredUser());

  function persistSession(token: string, user: User) {
    localStorage.setItem("testpilot_token", token);
    localStorage.setItem("testpilot_user", JSON.stringify(user));
    setUser(user);
  }

  async function login(email: string, password: string) {
    try {
      const { data } = await apiClient.post("/api/auth/login", { email, password });
      persistSession(data.access_token, data.user);
    } catch (error) {
      throw new Error(apiErrorMessage(error, "Login failed."));
    }
  }

  async function register(name: string, email: string, password: string) {
    try {
      const { data } = await apiClient.post("/api/auth/register", { name, email, password });
      persistSession(data.access_token, data.user);
    } catch (error) {
      throw new Error(apiErrorMessage(error, "Registration failed."));
    }
  }

  function logout() {
    localStorage.removeItem("testpilot_token");
    localStorage.removeItem("testpilot_user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider.");
  }
  return context;
}
