import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useAuth, homeFor } from "@/lib/auth";
import { Loader2 } from "lucide-react";

export const Route = createFileRoute("/")({
  component: RootIndexConduit,
});

function RootIndexConduit() {
  const { user, ready } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // 🛡️ Traffic Control Gate: Only execute routing after Firebase checks the active session
    if (ready) {
      if (user) {
        // Option A: Logged In -> Forward instantly to their designated home panel
        navigate({ to: homeFor(user.role), replace: true });
      } else {
        // Option B: No Session -> Route silently to the multi-tenant Auth Hub
        navigate({ to: "/auth", replace: true });
      }
    }
  }, [ready, user, navigate]);

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-[#020617] text-white">
      <div className="text-center space-y-3">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-amber-400" />
        <p className="text-xs font-semibold text-slate-400 tracking-wider uppercase">
          Initializing Helpdesk Routing Systems...
        </p>
      </div>
    </div>
  );
}
