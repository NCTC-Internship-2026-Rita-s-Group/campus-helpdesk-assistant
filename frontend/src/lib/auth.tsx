import React, { createContext, useContext, useState, useEffect } from "react";
import {
  onAuthStateChanged,
  signOut as firebaseSignOut,
  User as FirebaseUser,
} from "firebase/auth";
import { auth } from "./firebase";

// Define the clear role tracking parameters
export type Role = "admin" | "student";

export interface AuthUser {
  email: string | null;
  name: string | null;
  role: Role;
  token: string | null;
  username?: string;
}

interface AuthContextType {
  // 🪐 Backward-Compatible Naming Matrix
  user: AuthUser | null; // Matches auth.tsx login expectations
  profile: AuthUser | null; // Matches _authenticated.tsx layout expectations
  ready: boolean; // true when Firebase finishes checking session tracks
  loading: boolean; // true when checking session tracking (opposite of ready)
  setAuthenticatedUser: (user: AuthUser | null) => void;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 👑 1. THE MISSING EXPORT RESOLVED
// This utility resolves explicit route targeting string paths dynamically across the workspace
export function homeFor(role: Role | string | undefined | null): string {
  if (!role) return "/auth";
  const cleanRole = role.toLowerCase();
  if (cleanRole === "admin") return "/admin/dashboard";
  return "/student/chat";
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [isReady, setIsReady] = useState<boolean>(false);

  useEffect(() => {
    // Synchronize listener hooks straight with active Firebase client workers
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      try {
        if (firebaseUser) {
          // Pull existing role attributes out of session cache keys if manually authenticated
          const tokenResult = await firebaseUser.getIdTokenResult();
          const roleFromClaim = tokenResult.claims.role as Role;

          // Fallback checking email domain configurations if token parameters haven't refreshed
          const derivedRole: Role =
            roleFromClaim ||
            (firebaseUser.email?.endsWith("@amity.edu") ||
            firebaseUser.email === "prakashvvk020@gmail.com"
              ? "admin"
              : "student");

          const idToken = await firebaseUser.getIdToken();

          setCurrentUser({
            email: firebaseUser.email,
            name:
              firebaseUser.displayName ||
              (derivedRole === "admin" ? "Systems Administrator" : "Student"),
            role: derivedRole,
            token: idToken,
          });
        } else {
          setCurrentUser(null);
        }
      } catch (err) {
        console.error("❌ Firebase authentication synchronization track fault:", err);
        setCurrentUser(null);
      } finally {
        setIsReady(true);
      }
    });

    return () => unsubscribe();
  }, []);

  const setAuthenticatedUser = (user: AuthUser | null) => {
    setCurrentUser(user);
  };

  const handleSignOut = async () => {
    await firebaseSignOut(auth);
    setCurrentUser(null);
  };

  // Provide an overloaded context value object that fulfills both variable naming schemes
  const contextualPropertiesValue: AuthContextType = {
    user: currentUser,
    profile: currentUser, // Mirrors the object state to satisfy .profile lookups
    ready: isReady,
    loading: !isReady, // Inverts the status flag to satisfy .loading lookups cleanly
    setAuthenticatedUser,
    signOut: handleSignOut,
  };

  return <AuthContext.Provider value={contextualPropertiesValue}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider context shell boundary layer.");
  }
  return context;
}
