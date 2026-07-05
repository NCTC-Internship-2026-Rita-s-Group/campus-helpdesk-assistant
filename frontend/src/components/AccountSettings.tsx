import React, { useState } from "react";
import { EmailAuthProvider, reauthenticateWithCredential, updatePassword } from "firebase/auth";
import { auth } from "../lib/firebase";
import { toast } from "sonner";
import { KeyRound, Eye, EyeOff, X, Loader2, CheckCircle2, ShieldAlert } from "lucide-react";
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

  // 👑 INDEPENDENT CONTROLLERS: Separates tracking variables to prevent simultaneous unmasking glitches
  const [showCurrentPassword, setShowCurrentPassword] = useState<boolean>(false);
  const [showNewPassword, setShowNewPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);

  if (!isOpen) return null;

  // Unified panel teardown sequence to secure parameters out of memory on exit
  const handleSecureClose = () => {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setShowCurrentPassword(false);
    setShowNewPassword(false);
    setShowConfirmPassword(false);
    onClose();
  };

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
      handleSecureClose();
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
      {/* High-Contrast Morphic Glass Canvas */}
      <div className="glass-panel w-full max-w-md rounded-2xl border border-white/10 bg-[#020b1e] p-6 shadow-2xl relative animate-scale-in">
        {/* Absolute Top-Right Dismissal Anchor Button */}
        <button
          type="button"
          onClick={handleSecureClose}
          className="absolute top-4 right-4 rounded-lg p-1.5 text-slate-400 hover:bg-white/5 hover:text-white transition-all outline-none"
          title="Dismiss settings panel"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Branding Sub-Header Matrix */}
        <div className="flex items-center gap-3 border-b border-white/5 pb-4 mb-5">
          <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-2 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.1)]">
            <KeyRound className="h-5 w-5" />
          </div>
          <div className="text-left">
            <h3 className="text-lg font-semibold text-white tracking-tight">
              Account Security Settings
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Mutate credential secret access tokens</p>
          </div>
        </div>

        {/* Interactive Mutation Form Thread */}
        <form onSubmit={handlePasswordMutation} className="space-y-4">
          {/* FIELD 1: VERIFY CURRENT PASSWORD */}
          <div className="space-y-1.5 text-left">
            <Label
              htmlFor="curr-pass"
              className="text-slate-300 text-xs font-semibold tracking-wide"
            >
              Verify Current Password
            </Label>
            <div className="relative">
              <Input
                id="curr-pass"
                type={showCurrentPassword ? "text" : "password"}
                placeholder="••••••••"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="h-11 border-white/10 bg-black/40 text-white pr-10 placeholder:text-slate-600 focus-visible:ring-amber-500/50 font-sans tracking-wide"
                required
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors p-1 rounded-md outline-none"
                title={showCurrentPassword ? "Hide password" : "Show password"}
              >
                {showCurrentPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* FIELD 2: TARGET NEW PASSWORD */}
          <div className="space-y-1.5 text-left">
            <Label
              htmlFor="new-pass"
              className="text-slate-300 text-xs font-semibold tracking-wide"
            >
              Target New Password
            </Label>
            <div className="relative">
              <Input
                id="new-pass"
                type={showNewPassword ? "text" : "password"}
                placeholder="Minimum 6 characters"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="h-11 border-white/10 bg-black/40 text-white pr-10 placeholder:text-slate-600 focus-visible:ring-amber-500/50 font-sans tracking-wide"
                required
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors p-1 rounded-md outline-none"
                title={showNewPassword ? "Hide password" : "Show password"}
              >
                {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* FIELD 3: CONFIRM TARGET PASSWORD MATCH */}
          <div className="space-y-1.5 text-left">
            <Label
              htmlFor="conf-pass"
              className="text-slate-300 text-xs font-semibold tracking-wide"
            >
              Confirm Target Password
            </Label>
            <div className="relative">
              <Input
                id="conf-pass"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="h-11 border-white/10 bg-black/40 text-white pr-10 placeholder:text-slate-600 focus-visible:ring-amber-500/50 font-sans tracking-wide"
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors p-1 rounded-md outline-none"
                title={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Federated Sign-On Context Callout Indicator Box */}
          <div className="text-[10px] leading-normal text-slate-400 bg-white/[0.01] border border-white/5 rounded-xl p-3 select-none flex gap-2 items-start">
            <ShieldAlert className="h-3.5 w-3.5 text-slate-500 shrink-0 mt-0.5" />
            <p>
              Note: Access keys require valid credential validation. Google OAuth profiles can
              establish an email login password directly via this secure session node.
            </p>
          </div>

          {/* Form Modal Foot Controls Array */}
          <div className="flex gap-3 pt-2 border-t border-white/5">
            <Button
              type="button"
              variant="outline"
              onClick={handleSecureClose}
              className="flex-1 border-white/10 bg-transparent hover:bg-white/5 h-10 text-xs text-slate-200 font-semibold transition-all rounded-xl active:scale-[0.98]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-amber-400 text-slate-950 font-bold hover:brightness-110 h-10 text-xs rounded-xl active:scale-[0.98] transition-all flex items-center justify-center gap-1.5"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin mr-1 text-slate-950" />{" "}
                  Re-Authorizing...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 stroke-[2.5]" /> Update Secrets
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
