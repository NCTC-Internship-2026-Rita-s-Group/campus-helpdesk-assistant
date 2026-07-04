import { Link, useNavigate, useLocation } from "@tanstack/react-router";
import { LogOut, MessageSquareCode, Bell, Ticket, ShieldCheck, Sparkles } from "lucide-react"; // 🚀 Added Sparkles import
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export function AppHeader() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Set default brand anchor path based on active user role clearance
  const home = user?.role?.toLowerCase() === "admin" ? "/admin/dashboard" : "/student/chat";

  // Helper utility to highlight the active tab matching the current URL path
  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 w-full">
      <div className="glass-panel mx-auto mt-3 flex w-[calc(100%-1.5rem)] max-w-7xl items-center justify-between rounded-2xl px-4 py-2.5 sm:px-6">
        {/* Left Section: Branding Logo */}
        <Link
          to={home}
          className="group flex items-center gap-3 outline-none"
          aria-label="Go to home"
        >
          <div className="relative grid h-11 w-11 shrink-0 place-items-center rounded-full bg-white/90 p-1.5 ring-1 ring-[color:var(--gold)]/40 shadow-[0_0_24px_-6px_oklch(0.83_0.17_86/0.6)]">
            <img
              src="/logo.png"
              alt="Amity University Jharkhand"
              className="h-full w-full object-contain"
            />
          </div>
          <div className="hidden flex-col leading-tight md:flex">
            <span className="font-display text-[15px] font-bold tracking-wide text-white">
              Amity University
            </span>
            <span className="text-[10px] uppercase tracking-[0.18em] text-[color:var(--gold)]">
              Helpdesk · Jharkhand
            </span>
          </div>
        </Link>

        {/* Center Section: Adaptive Navigation Deck */}
        {user && (
          <nav className="flex items-center gap-1 rounded-xl bg-black/20 p-1 border border-white/5 backdrop-blur-sm sm:gap-2">
            {/* 👨‍🎓 STUDENT SPECIFIC LINKS */}
            {user.role?.toLowerCase() === "student" && (
              <>
                <Link
                  to="/student/chat"
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold tracking-wide transition-all sm:text-sm ${
                    isActive("/student/chat")
                      ? "bg-[color:var(--gold)] text-slate-950 shadow-md"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <MessageSquareCode className="h-4 w-4 shrink-0" />
                  <span className="hidden sm:inline">Assistant Chat</span>
                </Link>

                <Link
                  to="/student/notices"
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold tracking-wide transition-all sm:text-sm ${
                    isActive("/student/notices")
                      ? "bg-[color:var(--gold)] text-slate-950 shadow-md"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <Bell className="h-4 w-4 shrink-0" />
                  <span className="hidden sm:inline">Bulletin Board</span>
                </Link>

                <Link
                  to="/student/tickets"
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold tracking-wide transition-all sm:text-sm ${
                    isActive("/student/tickets")
                      ? "bg-[color:var(--gold)] text-slate-950 shadow-md"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <Ticket className="h-4 w-4 shrink-0" />
                  <span className="hidden sm:inline">Ticket Ledger</span>
                </Link>
              </>
            )}

            {/* 🛡️ ADMINISTRATIVE OPERATIONS LINKS (Unified Side-by-Side Viewport Layout) */}
            {user.role?.toLowerCase() === "admin" && (
              <>
                {/* A. Operational Dashboard Gateway Anchor */}
                <Link
                  to="/admin/dashboard"
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold tracking-wide transition-all sm:text-sm ${
                    isActive("/admin/dashboard")
                      ? "bg-[color:var(--gold)] text-slate-950 shadow-md"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <ShieldCheck className="h-4 w-4 shrink-0" />
                  <span className="hidden sm:inline">Control Terminal</span>
                </Link>

                {/* B. Newly Mounted Sandbox Chat Testing Matrix Anchor */}
                <Link
                  to="/admin/chat"
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold tracking-wide transition-all sm:text-sm ${
                    isActive("/admin/chat")
                      ? "bg-[color:var(--gold)] text-slate-950 shadow-md"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <Sparkles className="h-4 w-4 shrink-0" />
                  <span className="hidden sm:inline">Assistant Chat</span>
                </Link>
              </>
            )}
          </nav>
        )}

        {/* Right Section: User Profile & Authentication Controls */}
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <div className="hidden flex-col items-end leading-tight sm:flex">
                <span className="text-sm font-medium text-white">{user.name}</span>
                <span className="text-[10px] uppercase tracking-[0.18em] text-[color:var(--gold)] font-bold">
                  {user.role}
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/5 hover:text-[color:var(--gold)] rounded-xl"
                onClick={() => {
                  signOut();
                  navigate({ to: "/auth" });
                }}
              >
                <LogOut className="mr-1.5 h-4 w-4" />
                Sign out
              </Button>
            </>
          ) : (
            <Link
              to="/auth"
              className="rounded-xl border border-[color:var(--gold)]/40 px-4 py-1.5 text-sm font-medium text-[color:var(--gold)] transition hover:bg-[color:var(--gold)]/10 bg-[#001A4D]/20 backdrop-blur-md"
            >
              Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

export function AmbientBackdrop() {
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden opacity-[0.06]"
    >
      <svg
        viewBox="0 0 800 800"
        className="absolute left-1/2 top-1/2 h-[120vmax] w-[120vmax] -translate-x-1/2 -translate-y-1/2 animate-spin-slow"
        fill="none"
        stroke="currentColor"
      >
        <g className="text-[color:var(--gold)]">
          {Array.from({ length: 18 }).map((_, i) => (
            <circle
              key={i}
              cx="400"
              cy="400"
              r={40 + i * 18}
              strokeWidth="0.6"
              opacity={0.5 - i * 0.02}
            />
          ))}
          {Array.from({ length: 24 }).map((_, i) => {
            const a = (i / 24) * Math.PI * 2;
            return (
              <line
                key={i}
                x1="400"
                y1="400"
                x2={400 + Math.cos(a) * 380}
                y2={400 + Math.sin(a) * 380}
                strokeWidth="0.4"
              />
            );
          })}
        </g>
      </svg>
    </div>
  );
}
