import { createFileRoute, Outlet, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Lock, LogOut } from "lucide-react";
import { AmbientBackdrop, AppHeader } from "@/components/AppHeader";
import { useAuth } from "@/lib/auth";
import { AccountSettings } from "@/components/AccountSettings"; // 🔑 Ingesting Phase 4 Security core modal

export const Route = createFileRoute("/_authenticated")({
  component: AuthenticatedLayout,
});

function AuthenticatedLayout() {
  const { user, ready, signOut } = useAuth();
  const navigate = useNavigate();

  // 🎛️ Phase 4 Settings Panel Toggle Controls State
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  useEffect(() => {
    if (ready && !user) navigate({ to: "/auth", replace: true });
  }, [ready, user, navigate]);

  if (!ready || !user) {
    return (
      <div className="relative min-h-screen">
        <AmbientBackdrop />
        <AppHeader />
        <div className="mx-auto max-w-7xl px-6 py-16">
          <div className="glass-panel h-64 animate-pulse rounded-3xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen">
      <AmbientBackdrop />
      <AppHeader />

      {/* Target views (Chat Sandbox, Notice board feed, or Admin control panels) render cleanly here */}
      <Outlet />

      {/* 👑 ENTERPRISE FLOATING SYSTEM SECURITY ANCHOR BAR */}
      {/* Sits elegantly out-of-bounds in the window margin layer to give fast password management controls */}
      <div className="fixed bottom-6 right-6 z-40 flex items-center gap-2 animate-fade-in">
        <button
          type="button"
          onClick={() => setIsSettingsOpen(true)}
          className="flex h-10 items-center gap-2 rounded-xl border border-white/10 bg-slate-900/80 px-4 text-xs font-bold text-slate-200 backdrop-blur-md transition-all hover:border-[color:var(--gold)]/40 hover:text-[color:var(--gold)] active:scale-95 shadow-lg shadow-black/40"
          title="Security Controls Matrix"
        >
          <Lock className="h-3.5 w-3.5 text-[color:var(--gold)]" />
          <span className="hidden sm:inline">Security Options</span>
        </button>

        <button
          type="button"
          onClick={() => {
            signOut();
            navigate({ to: "/auth", replace: true });
          }}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-slate-900/80 text-slate-400 backdrop-blur-md transition-all hover:border-rose-500/30 hover:text-rose-400 active:scale-95 shadow-lg shadow-black/40"
          title="Disconnect active profile session"
        >
          <LogOut className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* 🔐 PHASE 4 INTERACTIVE PASSWORD CHANGE WINDOW MODAL */}
      <AccountSettings isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  );
}
