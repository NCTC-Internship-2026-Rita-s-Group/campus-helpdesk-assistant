import React, { useState } from "react";
import { EmailAuthProvider, reauthenticateWithCredential, updatePassword } from "firebase/auth";
import { auth } from "../lib/firebase";
import { toast } from "sonner";
import { KeyRound, ShieldAlert, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface AccountSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AccountSettings: React.FC<AccountSettingsProps> = ({ isOpen, onClose }) => {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handlePasswordMutation = async (e: React.FormEvent) => {
    e.preventDefault();

    // 🛡️ Data Validation Guardrails
    if (newPassword.length < 6) {
      toast.error("Security baseline rule: New password must be at least 6 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("Mismatch detected: Confirm password field must match the new target key.");
      return;
    }

    const activeUser = auth.currentUser;
    if (!activeUser || !activeUser.email) {
      toast.error("Session missing: Identity context cannot be resolved.");
      return;
    }

    setLoading(true);
    try {
      // 1. Re-authenticate user session context prior to committing mutation loops
      const credential = EmailAuthProvider.credential(activeUser.email, currentPassword);
      await reauthenticateWithCredential(activeUser, credential);

      // 2. Commit the new secret token keys down to the authentication server
      await updatePassword(activeUser, newPassword);

      toast.success("Security keys modified successfully across all ledger channels.");

      // Clear forms out safely
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      onClose();
    } catch (err: any) {
      console.error("❌ Password Mutation Exception Layer:", err);
      if (err.code === "auth/wrong-password") {
        toast.error("Re-authentication rejected: Current password input is invalid.");
      } else {
        toast.error(err.message || "Failed to commit security signature updates.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in p-4">
      <div className="glass-panel w-full max-w-md rounded-2xl border border-white/10 bg-slate-950 p-6 shadow-2xl relative">
        <div className="flex items-center gap-3 border-b border-white/5 pb-4 mb-5">
          <div className="rounded-lg bg-[color:var(--gold)]/10 p-2 text-[color:var(--gold)]">
            <KeyRound className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">Account Security settings</h3>
            <p className="text-xs text-muted-foreground">Mutate credential secret access tokens</p>
          </div>
        </div>

        <form onSubmit={handlePasswordMutation} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="curr-pass" className="text-foreground/80 text-xs">
              Verify Current Password
            </Label>
            <Input
              id="curr-pass"
              type="password"
              placeholder="••••••••"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="h-10 border-white/10 bg-white/5 text-foreground placeholder:text-foreground/30 focus-visible:ring-[color:var(--gold)]/50"
              required
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="new-pass" className="text-foreground/80 text-xs">
              Target New Password
            </Label>
            <Input
              id="new-pass"
              type="password"
              placeholder="••••••••"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="h-10 border-white/10 bg-white/5 text-foreground placeholder:text-foreground/30 focus-visible:ring-[color:var(--gold)]/50"
              required
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="conf-pass" className="text-foreground/80 text-xs">
              Confirm Target Password
            </Label>
            <Input
              id="conf-pass"
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="h-10 border-white/10 bg-white/5 text-foreground placeholder:text-foreground/30 focus-visible:ring-[color:var(--gold)]/50"
              required
            />
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1 border-white/10 bg-transparent hover:bg-white/5 h-10 text-xs text-foreground font-medium"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-[color:var(--gold)] text-[color:var(--gold-foreground)] font-semibold hover:bg-[color:var(--gold)]/90 h-10 text-xs"
            >
              {loading ? "Re-Authorizing..." : "Update Secrets"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
