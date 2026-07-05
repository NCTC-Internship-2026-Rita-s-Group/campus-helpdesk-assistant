import React, { createContext, useContext, useState, useEffect } from "react";
import {
  onAuthStateChanged,
  signOut as firebaseSignOut,
  User as FirebaseUser,
  sendPasswordResetEmail,
  confirmPasswordReset,
  sendEmailVerification,
} from "firebase/auth";
import { auth } from "./firebase";
import { toast } from "sonner";

export type Role = "admin" | "student";

export interface AuthUser {
  email: string | null;
  name: string | null;
  role: Role;
  token: string | null;
  username?: string;
  emailVerified: boolean; // 🔒 Added for strict multi-factor verification checks
}

interface AuthContextType {
  user: AuthUser | null;
  profile: AuthUser | null;
  ready: boolean;
  loading: boolean;
  setAuthenticatedUser: (user: AuthUser | null) => void;
  signOut: () => Promise<void>;

  // 👑 PRODUCTION AUTH LIFECYCLE EXTENSIONS
  triggerPasswordReset: (email: string) => Promise<void>;
  resolvePasswordReset: (actionCode: string, newPassword: string) => Promise<void>;
  dispatchVerificationEmail: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

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
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      try {
        if (firebaseUser) {
          const tokenResult = await firebaseUser.getIdTokenResult();
          const roleFromClaim = tokenResult.claims.role as Role;

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
            emailVerified: firebaseUser.emailVerified, // 🛡️ Live verification tracking state synced from Firebase core
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

  /**
   * 📧 1. OUT-OF-BOUND PASSWORD RESET DISPATCHER
   * Requests a secure, uniquely signed recovery token from Firebase and streams it to the user's inbox.
   */
  const triggerPasswordReset = async (email: string) => {
    try {
      // Direct integration with standard institutional reset action parameters
      const actionCodeSettings = {
        url: window.location.origin + "/auth?mode=signin", // Redirect target once password adjustment settles
        handleCodeInApp: true,
      };
      await sendPasswordResetEmail(auth, email.trim(), actionCodeSettings);
      toast.success("Security token successfully routed to your email inbox.");
    } catch (err: any) {
      console.error("❌ Reset link configuration failure:", err);
      throw new Error(err.message || "Failed to trigger recovery sequence.");
    }
  };

  /**
   * 🔒 2. ACTION CODE CONFIRMATION RESOLVER
   * Intercepts the action code parameter returned from the email link and executes password updates safely.
   */
  const resolvePasswordReset = async (actionCode: string, newPassword: string) => {
    try {
      await confirmPasswordReset(auth, actionCode, newPassword.trim());
      toast.success("Access keys updated. Please log in using your new password.");
    } catch (err: any) {
      console.error("❌ Code verification failure:", err);
      throw new Error(err.message || "The security reset code has expired or is invalid.");
    }
  };

  /**
   * 🛡️ 3. LIVE EMAIL VERIFICATION MONITOR
   * Pushes a verification link straight to an active user session to confirm email legitimacy.
   */
  const dispatchVerificationEmail = async () => {
    if (!auth.currentUser) {
      toast.error("Active user session required to request verification tokens.");
      return;
    }
    try {
      await sendEmailVerification(auth.currentUser);
      toast.info("A new verification code has been dispatched to your email address.");
    } catch (err: any) {
      console.error("❌ Verification deployment crash:", err);
      throw new Error(err.message || "Email validation link could not be deployed.");
    }
  };

  const contextualPropertiesValue: AuthContextType = {
    user: currentUser,
    profile: currentUser,
    ready: isReady,
    loading: !isReady,
    setAuthenticatedUser,
    signOut: handleSignOut,
    triggerPasswordReset, // Expose to layout components safely
    resolvePasswordReset, // Expose to layout components safely
    dispatchVerificationEmail, // Expose to layout components safely
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
