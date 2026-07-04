import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { GraduationCap, ShieldCheck, Sparkles, ArrowLeft, Mail, Eye, EyeOff } from "lucide-react";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signInWithCustomToken,
  sendPasswordResetEmail,
} from "firebase/auth";
import { auth } from "../lib/firebase";
import { apiClient } from "../lib/api";
import { AmbientBackdrop } from "@/components/AppHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth, homeFor, type Role } from "@/lib/auth";

export const Route = createFileRoute("/auth")({
  head: () => ({
    meta: [
      { title: "Gateway · Amity Helpdesk" },
      {
        name: "description",
        content: "Secure access control node for Amity University Jharkhand helpdesk workspace.",
      },
    ],
  }),
  component: AuthPage,
});

function AuthPage() {
  const { user, ready, setAuthenticatedUser } = useAuth();
  const navigate = useNavigate();

  // High-Level Viewport Controllers
  const [role, setRole] = useState<Role>("student");
  const [studentFlow, setStudentFlow] = useState<"options" | "email_form" | "forgot">("options");
  const [mode, setMode] = useState<"signin" | "signup">("signin");

  // Visibility State Controller Matrix
  const [showPassword, setShowPassword] = useState<boolean>(false);

  // Input Binding State Fields
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  // Sync tab switching behaviors cleanly
  useEffect(() => {
    setStudentFlow("options");
    setMode("signin");
    setShowPassword(false);
  }, [role]);

  // 🛡️ FIXED: Session Interceptor optimized to prevent redirection race conditions during manual active submissions
  useEffect(() => {
    if (ready && user && !authLoading && studentFlow === "options") {
      navigate({ to: homeFor(user.role), replace: true });
    }
  }, [ready, user, authLoading, studentFlow, navigate]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);

    try {
      if (role === "student") {
        let userCredential;
        if (mode === "signup") {
          userCredential = await createUserWithEmailAndPassword(auth, email, password);
          toast.success(
            "Identity registration confirmed. Synchronizing local workspace records...",
          );
        } else {
          userCredential = await signInWithEmailAndPassword(auth, email, password);
        }

        const idToken = await userCredential.user.getIdToken();
        const syncProfile = await apiClient.syncUserSession(idToken);

        setAuthenticatedUser({
          email: syncProfile.email,
          name: syncProfile.name,
          role: syncProfile.role as Role,
          token: idToken,
        });

        toast.success(`Access Clear: Welcome ${syncProfile.name}`);
        navigate({ to: syncProfile.redirect_target, replace: true });
      } else {
        if (!username.trim()) {
          toast.error("Administrative authentication requires a valid username or email address.");
          setAuthLoading(false);
          return;
        }

        const adminAuthData = await apiClient.adminLogin(username.trim(), password);
        const userCredential = await signInWithCustomToken(auth, adminAuthData.custom_token);
        const freshJwtToken = await userCredential.user.getIdToken();

        setAuthenticatedUser({
          email: adminAuthData.email,
          name: adminAuthData.name,
          role: adminAuthData.role as Role,
          token: freshJwtToken,
          username: username.trim(),
        });

        toast.success("Welcome back to your Admin Dashboard console.");
        // 🚀 FORCE DIRECTION TARGET FLUSH: Direct routing execution bypasses background state listeners cleanly
        navigate({ to: adminAuthData.redirect_target, replace: true });
      }
    } catch (error: any) {
      console.error("❌ Security Auth Flow Exception:", error);
      toast.error(error.message || "Invalid credentials configuration.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleInlinePasswordRecovery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes("@")) {
      toast.error("Valid email address required.");
      return;
    }

    setAuthLoading(true);
    try {
      await sendPasswordResetEmail(auth, email.trim());
      toast.success("Password recovery link has been pushed to your email inbox.");
      setStudentFlow("email_form");
      setMode("signin");
    } catch (err: any) {
      toast.error(err.message || "Failed to issue password recovery link.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setAuthLoading(true);
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      const idToken = await result.user.getIdToken();
      const syncProfile = await apiClient.syncUserSession(idToken);

      setAuthenticatedUser({
        email: syncProfile.email,
        name: syncProfile.name,
        role: syncProfile.role as Role,
        token: idToken,
      });

      toast.success("Google sign-on synchronization mapped successfully.");
      navigate({ to: syncProfile.redirect_target, replace: true });
    } catch (error: any) {
      console.error("❌ Federated SSO Fault:", error);
      toast.error(error.message || "Google single sign-on pipeline aborted.");
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#030712] text-white selection:bg-amber-500/30">
      <AmbientBackdrop />

      {/* 🌌 ORIGINAL HIGH-VISIBILITY UNIVERSITY BRANDING HEADER */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#030712]/60 border-b border-white/5 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-400 p-0.5 font-bold text-slate-950 flex items-center justify-center tracking-wider text-sm shadow-md">
            AU
          </div>
          <div className="text-left">
            <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              Amity University{" "}
              <span className="text-[10px] text-amber-400 font-extrabold uppercase tracking-widest px-1.5 py-0.5 rounded bg-amber-400/10 border border-amber-400/20">
                Jharkhand
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">
              Verified Institutional AI Knowledge Hub
            </p>
          </div>
        </div>

        {role === "student" && studentFlow !== "forgot" && (
          <button
            type="button"
            onClick={() => {
              setMode(mode === "signin" ? "signup" : "signin");
              setStudentFlow("email_form");
              setShowPassword(false);
            }}
            className="text-xs font-semibold px-4 py-2 rounded-xl border border-white/10 bg-white/5 text-slate-200 hover:bg-white/10 hover:text-white transition-all active:scale-95 shadow-sm"
          >
            {mode === "signin" ? "Create an account" : "Sign In"}
          </button>
        )}
      </header>

      <main className="mx-auto grid max-w-7xl gap-8 px-6 py-10 md:grid-cols-2 md:gap-12 md:py-16 items-center">
        {/* Left Informational Showcase Panel */}
        <section className="glass-panel animate-fade-up flex flex-col justify-between rounded-3xl p-8 md:p-10 min-h-[460px]">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--gold)]/30 bg-[color:var(--gold)]/5 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-[color:var(--gold)]">
              <Sparkles className="h-3.5 w-3.5" />
              Autonomous RAG
            </div>
            <h1 className="mt-6 font-display text-4xl font-bold leading-tight text-foreground md:text-5xl text-left">
              The intelligent helpdesk for{" "}
              <span className="text-[color:var(--gold)]">Amity University</span> Jharkhand.
            </h1>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground text-left">
              Verify regulatory circulars, track student grievance lifecycles, and stream vectorized
              documentation nodes natively.
            </p>
          </div>

          <ul className="mt-10 grid gap-3 text-left">
            {[
              "24/7 Digital Campus Assistant — Get immediate, intelligent guidance on university schedules, exam timetables, and department criteria instantly.",
              "100% Verified University Information — Every analytical response is pulled directly from official Amity brochures, policy manuals, and academic circulars.",
              "Direct Support Desk Escalation — If your query requires manual administrative review, the system automatically files an official helpdesk ticket for you.",
            ].map((t) => (
              <li
                key={t}
                className="flex items-start gap-3 rounded-xl border border-white/5 bg-white/[0.02] p-3 text-sm text-foreground/90"
              >
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[color:var(--gold)] shadow-[0_0_10px_2px_oklch(0.83_0.17_86/0.6)]" />
                {t}
              </li>
            ))}
          </ul>
        </section>

        {/* Right Authentication Interactor Form Card */}
        <section className="glass-panel animate-fade-up rounded-3xl p-8 md:p-10 flex flex-col justify-center min-h-[460px]">
          {studentFlow !== "forgot" && (
            <div className="grid grid-cols-2 gap-1 rounded-2xl border border-white/5 bg-[color:var(--navy)]/40 p-1 mb-8 shrink-0">
              {(["student", "admin"] as Role[]).map((r) => {
                const active = role === r;
                const Icon = r === "student" ? GraduationCap : ShieldCheck;
                return (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setRole(r)}
                    className={
                      "flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition " +
                      (active
                        ? "bg-[color:var(--gold)] text-slate-950 font-bold shadow-lg"
                        : "text-foreground/70 hover:text-foreground")
                    }
                  >
                    <Icon className="h-4 w-4" />
                    {r === "student" ? "Student Hub" : "Admin Terminal"}
                  </button>
                );
              })}
            </div>
          )}

          <div className="text-left mb-6">
            <h2 className="font-display text-2xl font-semibold text-foreground">
              {role === "student"
                ? studentFlow === "forgot"
                  ? "Reset Password"
                  : mode === "signin"
                    ? "Student Login"
                    : "Create Student Account"
                : "Administrative Portal"}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {role === "student"
                ? studentFlow === "forgot"
                  ? "Receive a secure self-service password recovery link"
                  : "Access your student helpdesk context panel"
                : "Secure Operator Workspace Authorization"}
            </p>
          </div>

          {/* FLOW STEP 1: OPTIONS PANEL */}
          {role === "student" && studentFlow === "options" && (
            <div className="space-y-4 animate-fade-in">
              <Button
                type="button"
                onClick={handleGoogleSignIn}
                disabled={authLoading}
                className="w-full h-12 bg-white text-slate-950 font-bold hover:bg-slate-100 flex items-center justify-center gap-3 rounded-xl transition-all shadow-md active:scale-[0.99]"
              >
                <svg
                  className="h-4 w-4 shrink-0"
                  viewBox="0 0 24 24"
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M23.745,12.273 C23.745,11.482 23.673,10.718 23.545,9.982 L12,9.982 L12,14.327 L18.573,14.327 C18.291,15.773 17.473,17 16.245,17.836 L16.245,20.655 L19.991,20.655 C22.182,18.636 23.745,15.636 23.745,12.273 Z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12,24 C15.245,24 17.964,22.927 19.991,20.655 L16.245,17.836 C15.218,18.536 13.882,18.964 12,18.964 C8.873,18.964 6.227,16.855 5.282,14 L1.418,14 L1.418,17 C3.4,20.945 7.482,24 12,24 Z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.282,14 C5.036,13.273 4.9,12.5 4.9,11.7 C4.9,10.9 5.036,10.127 5.282,9.4 L5.282,6.4 L1.418,6.4 C0.518,8 0,9.8 0,11.7 C0,13.6 0.518,15.4 1.418,17 L5.282,14 Z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12,5.036 C13.773,5.036 15.355,5.645 16.609,6.845 L19.836,3.591 C17.955,1.836 15.236,0.764 12,0.764 C7.482,0.764 3.4,3.818 1.418,7.764 L5.282,10.764 C6.227,7.909 8.873,5.036 12,5.036 Z"
                    fill="#EA4335"
                  />
                </svg>
                Continue with Google
              </Button>

              <Button
                type="button"
                onClick={() => setStudentFlow("email_form")}
                className="w-full h-12 bg-[#1e293b]/60 border border-slate-700 text-white font-bold hover:bg-slate-800 flex items-center justify-center gap-3 rounded-xl transition-all active:scale-[0.99]"
              >
                <Mail className="h-4 w-4 text-amber-400" />
                Continue with Email
              </Button>
            </div>
          )}

          {/* FLOW STEP 2: RECOVERY MODULE */}
          {role === "student" && studentFlow === "forgot" && (
            <form
              onSubmit={handleInlinePasswordRecovery}
              className="space-y-4 text-left animate-fade-in"
            >
              <div className="space-y-1.5">
                <Label htmlFor="reset-email" className="text-foreground/80">
                  Email Address
                </Label>
                <Input
                  id="reset-email"
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-11 border-white/10 bg-white/5 text-white focus-visible:ring-[color:var(--gold)]/50"
                  required
                />
              </div>
              <Button
                type="submit"
                disabled={authLoading}
                className="w-full h-11 bg-[color:var(--gold)] text-slate-950 font-bold hover:bg-[color:var(--gold)]/90"
              >
                {authLoading ? "Issuing Link..." : "Send Reset Link"}
              </Button>
              <button
                type="button"
                onClick={() => setStudentFlow("email_form")}
                className="w-full flex items-center justify-center gap-2 text-xs text-muted-foreground hover:text-white transition-colors pt-2 font-medium"
              >
                <ArrowLeft className="h-3.5 w-3.5" /> Return to Login
              </button>
            </form>
          )}

          {/* FLOW STEP 3: CREDENTIAL FORMS */}
          {((role === "student" && studentFlow === "email_form") || role === "admin") && (
            <form onSubmit={onSubmit} className="space-y-4 text-left animate-fade-in">
              {role === "student" && mode === "signup" && (
                <div className="space-y-1.5 animate-fade-in">
                  <Label htmlFor="name" className="text-foreground/80">
                    Full Name
                  </Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="h-11 border-white/10 bg-white/5 text-white focus-visible:ring-[color:var(--gold)]/50"
                    required
                  />
                </div>
              )}

              {role === "student" ? (
                <div className="space-y-1.5">
                  <Label htmlFor="email" className="text-foreground/80">
                    Email Address
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11 border-white/10 bg-white/5 text-white focus-visible:ring-[color:var(--gold)]/50"
                    required
                  />
                </div>
              ) : (
                <div className="space-y-1.5">
                  <Label htmlFor="username" className="text-foreground/80">
                    Username or Email Address
                  </Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter username or admin email"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="h-11 border-white/10 bg-white/5 text-white focus-visible:ring-[color:var(--gold)]/50"
                    required
                  />
                </div>
              )}

              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <Label htmlFor="password" className="text-foreground/80">
                    Password
                  </Label>
                  {role === "student" && mode === "signin" && (
                    <span
                      onClick={() => setStudentFlow("forgot")}
                      className="text-xs text-[color:var(--gold)] hover:underline cursor-pointer font-medium"
                    >
                      Forgot Password?
                    </span>
                  )}
                </div>

                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11 border-white/10 bg-white/5 text-white pr-10 focus-visible:ring-[color:var(--gold)]/50 font-sans"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                    title={showPassword ? "Hide password" : "Reveal password"}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4.5 w-4.5" />
                    ) : (
                      <Eye className="h-4.5 w-4.5" />
                    )}
                  </button>
                </div>
              </div>

              {role === "admin" && (
                <p className="text-[11px] text-slate-400 bg-white/[0.02] border border-white/5 rounded-xl p-3 leading-normal animate-fade-in select-none">
                  🔒 <span className="font-bold text-slate-300">Security Directives Notice:</span>{" "}
                  Password recovery is restricted for administrative accounts. Please reach out to
                  your IT Systems Administrator for manual key re-assignments.
                </p>
              )}

              <Button
                type="submit"
                disabled={authLoading}
                className="mt-2 h-11 w-full bg-[color:var(--gold)] text-slate-950 font-bold hover:bg-[color:var(--gold)]/90 transition-colors shadow-md"
              >
                {authLoading
                  ? "Authorizing..."
                  : role === "student"
                    ? mode === "signin"
                      ? "Sign In"
                      : "Register Account"
                    : "Log In as Admin"}
              </Button>

              {role === "student" && (
                <div className="pt-2 text-center space-y-3">
                  <p className="text-xs text-muted-foreground">
                    {mode === "signin"
                      ? "New to the helpdesk system?"
                      : "Already possess an active profile?"}{" "}
                    <button
                      type="button"
                      onClick={() => {
                        setMode(mode === "signin" ? "signup" : "signin");
                        setShowPassword(false);
                      }}
                      className="text-[color:var(--gold)] hover:underline font-bold transition-all"
                    >
                      {mode === "signin" ? "Create an account" : "Sign in instead"}
                    </button>
                  </p>

                  <button
                    type="button"
                    onClick={() => setStudentFlow("options")}
                    className="flex items-center justify-center gap-1.5 text-xs text-slate-500 hover:text-white transition-colors mx-auto font-semibold"
                  >
                    <ArrowLeft className="h-3.5 w-3.5" /> Return to options
                  </button>
                </div>
              )}
            </form>
          )}
        </section>
      </main>
    </div>
  );
}
