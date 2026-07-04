import React, { createContext, useContext, useEffect, useState } from "react";
import { User, onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from "../lib/firebase";

// 📋 Declare what properties our components can read from the login state
interface UserProfile {
  id: number;
  email: string;
  name: string;
  role: "student" | "admin";
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  loading: boolean;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 📡 Set up a live observer thread targeting Firebase authentication states
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);

      // Dynamically grab the clean base URL from your .env.local file
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

      if (currentUser) {
        try {
          // 🪙 Fetch the dynamic cryptographically signed ID token string
          const token = await currentUser.getIdToken();

          // 🚀 Instantly synchronize session details with your local SQLite backend
          const response = await fetch(`${apiBaseUrl}/auth/me`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          });

          if (response.ok) {
            const profileData = await response.json();
            setProfile(profileData); // Safely hydrated with role info (student/admin)
          } else {
            console.error("⚠️ Failed to synchronize user profile ledger row from backend matrix.");
            setProfile(null);
          }
        } catch (error) {
          console.error("❌ Exception resolving authenticated handshake sync threads:", error);
          setProfile(null);
        }
      } else {
        setProfile(null);
      }

      setLoading(false);
    });

    return () => unsubscribe(); // Disconnect listener on component unmount
  }, []);

  const logout = async () => {
    setLoading(true);
    await signOut(auth);
    setUser(null);
    setProfile(null);
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{ user, profile, loading, logout }}>
      <children />
    </AuthContext.Provider>
  );
};

// 🪝 Reusable custom hook wrapper for instant context extraction across screens
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be executed within an active AuthProvider wrap node context.");
  }
  return context;
};
