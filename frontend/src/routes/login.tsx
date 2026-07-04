import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { ShieldCheck, User, Lock, Sparkles, Loader2, AlertCircle, ArrowRight } from "lucide-react";
import { useAuth } from "@/lib/auth";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [{ title: "Gateway Authentication · Amity Helpdesk" }],
  }),
  component: LoginComponent,
});

function LoginComponent() {
  const { login } = useAuth();
  const navigate = useNavigate();

  // Authentication Interface States
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [selectedRole, setSelectedRole] = useState<"student" | "admin">("student");
  const [loading, setLoading] = useState(false);
  const [errorAlert, setErrorAlert] = useState<string | null>(null);

  // Form Submittance Handler Pipeline
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorAlert(null);

    // Baseline validation check layers
    if (!email.trim() || !password.trim()) {
      setErrorAlert("Please populate all credential mapping segments.");
      return;
    }

    setLoading(true);

    // Simulated network authentication window handshake
    setTimeout(async () => {
      try {
        // Pushes credentials straight to your useAuth context layer
        const success = await login(email, password, selectedRole);

        if (success) {
          setLoading(false);
          toast.success(`Welcome back! Session authorized as ${selectedRole.toUpperCase()}`);

          // Role-targeted gateway path dispatching
          if (selectedRole === "admin") {
            navigate({ to: "/admin/dashboard" });
          } else {
            navigate({ to: "/student/chat" });
          }
        } else {
          throw new Error("Invalid credential handshake flags.");
        }
      } catch (err) {
        setLoading(false);
        setErrorAlert(
          "Authentication failed. Verify your campus credentials and system clearance layer.",
        );
      }
    }, 1200);
  };

  // Quick-Test Auto Populate Shortcut Matrix
  const fillMockCredentials = (role: "student" | "admin") => {
    setSelectedRole(role);
    if (role === "admin") {
      setEmail("admin.helpdesk@amity.edu");
      setPassword("••••••••");
    } else {
      setEmail("student.portal@amity.edu");
      setPassword("••••••••");
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#00061A] text-white flex items-center justify-center p-4 relative overflow-hidden font-sans">
      {/* Dynamic Aesthetic Backdrop Nebula Rings */}
      <div className="absolute top-[-20%] left-[-10%] w-[60rem] h-[60rem] bg-blue-950/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50rem] h-[50rem] bg-amber-950/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Primary Structural Authentication Card Panel */}
      <div className="w-full max-w-5xl rounded-3xl border border-white/10 bg-[#001433]/30 backdrop-blur-xl shadow-2xl grid md:grid-cols-12 overflow-hidden items-stretch min-h-[36rem]">
        {/* LEFT COMPONENT COLUMN: Branding Presentation Panel (5 Columns) */}
        <div className="md:col-span-5 bg-gradient-to-br from-[#001F4D] to-[#000E2B] p-8 flex flex-col justify-between relative border-b md:border-b-0 md:border-r border-white/10 text-left">
          <div className="space-y-6">
            {/* Branding Emblem Node */}
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-amber-500/10 p-2.5 border border-amber-500/20 text-[color:var(--gold)] shadow-[0_0_15px_rgba(245,158,11,0.15)]">
                <ShieldCheck className="h-6 w-6 stroke-[2]" />
              </div>
              <div>
                <h2 className="font-display text-lg font-bold tracking-tight leading-none text-white">
                  Amity University
                </h2>
                <span className="text-[10px] uppercase tracking-widest font-mono text-[color:var(--gold)] font-bold">
                  Helpdesk Core
                </span>
              </div>
            </div>

            <div className="space-y-3 pt-6">
              <h1 className="font-display text-2xl font-bold tracking-tight leading-tight">
                Enterprise <span className="text-[color:var(--gold)]">RAG Pipeline</span> Access
                Node
              </h1>
              <p className="text-xs text-slate-400 leading-relaxed">
                Log in to tap into centralized cognitive vector indexing routers. Students gain live
                conversational support, while operators govern active systemic queues.
              </p>
            </div>
          </div>

          {/* Quick Mock Testing Assistant Desk Footer */}
          <div className="pt-8 border-t border-white/5 space-y-2.5">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 font-mono flex items-center gap-1.5">
              <Sparkles className="h-3 w-3 text-[color:var(--gold)]" /> Prototyping Sandbox
              Bypasses:
            </span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => fillMockCredentials("student")}
                className="rounded-xl bg-white/5 border border-white/5 py-2 px-3 text-[11px] font-semibold text-slate-300 hover:bg-white/10 hover:text-white transition-all text-center"
              >
                Mock Student Mode
              </button>
              <button
                type="button"
                onClick={() => fillMockCredentials("admin")}
                className="rounded-xl bg-white/5 border border-white/5 py-2 px-3 text-[11px] font-semibold text-slate-300 hover:bg-white/10 hover:text-white transition-all text-center"
              >
                Mock Admin Mode
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT COMPONENT COLUMN: Core Interactive Auth Submission Matrix (7 Columns) */}
        <div className="md:col-span-7 p-8 sm:p-10 flex flex-col justify-center text-left space-y-6 bg-black/10">
          <div className="space-y-1">
            <h2 className="font-display text-xl font-bold text-slate-100">
              Gateway Authentication
            </h2>
            <p className="text-xs text-slate-400">
              Initialize credential tracking schemas to establish network session channels.
            </p>
          </div>

          {/* Active Error Alert Node Block */}
          {errorAlert && (
            <div className="flex items-start gap-2 rounded-xl border border-rose-500/20 bg-rose-500/10 p-3.5 text-xs text-rose-300 animate-fade-in">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <p className="leading-relaxed font-medium">{errorAlert}</p>
            </div>
          )}

          <form onSubmit={handleAuthSubmit} className="space-y-4">
            {/* 🔄 ROLE SELECTOR TAB GRID MATRIX */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
                Select Profile Clearance Layer
              </label>
              <div className="grid grid-cols-2 gap-2 bg-black/30 border border-white/10 p-1.5 rounded-xl">
                <button
                  type="button"
                  onClick={() => setSelectedRole("student")}
                  className={`rounded-lg py-2.5 text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                    selectedRole === "student"
                      ? "bg-[color:var(--gold)] text-slate-950 shadow-md"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <User className="h-3.5 w-3.5" />
                  Student Portal
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedRole("admin")}
                  className={`rounded-lg py-2.5 text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                    selectedRole === "admin"
                      ? "bg-[color:var(--gold)] text-slate-950 shadow-md"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <ShieldCheck className="h-3.5 w-3.5" />
                  Admin Terminal
                </button>
              </div>
            </div>

            {/* Email/ID Form Field Ingestion */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">
                Campus Email or Enrollment Token
              </label>
              <div className="relative flex items-center">
                <User className="absolute left-4 h-4 w-4 text-slate-500 pointer-events-none" />
                <input
                  type="text"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={
                    selectedRole === "admin"
                      ? "e.g., administrator@amity.edu"
                      : "e.g., student.enrollment@s.amity.edu"
                  }
                  className="w-full rounded-xl bg-black/20 border border-white/10 pl-11 pr-4 py-3 text-sm text-white placeholder-slate-600 outline-none focus:border-[color:var(--gold)]/50 transition-colors"
                />
              </div>
            </div>

            {/* Password Form Field Ingestion */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-xs font-medium text-slate-300">
                  Profile Security Password
                </label>
                <a
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    toast("Contact system administrator desk.");
                  }}
                  className="text-[11px] text-[color:var(--gold)]/70 hover:underline"
                >
                  Forgot?
                </a>
              </div>
              <div className="relative flex items-center">
                <Lock className="absolute left-4 h-4 w-4 text-slate-500 pointer-events-none" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full rounded-xl bg-black/20 border border-white/10 pl-11 pr-4 py-3 text-sm text-white placeholder-slate-600 outline-none focus:border-[color:var(--gold)]/50 transition-colors"
                />
              </div>
            </div>

            {/* Main Action Call Dispatch Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full font-bold text-sm rounded-xl py-3.5 bg-gradient-to-r from-[color:var(--gold)] to-amber-400 border border-amber-500/20 text-slate-950 hover:brightness-110 active:scale-[0.99] transition-all flex items-center justify-center gap-2 shadow-xl shadow-amber-500/5 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 Jack-spin animate-spin" />
                    Authorizing Ledger Credentials...
                  </>
                ) : (
                  <>
                    Establish Secure Session
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
