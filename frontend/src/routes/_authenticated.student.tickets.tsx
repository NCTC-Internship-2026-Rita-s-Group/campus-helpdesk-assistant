import { createFileRoute } from "@tanstack/react-router";
import { AlertCircle, CheckCircle2, Clock, FileText, Plus, Loader2, X } from "lucide-react";
import { useState, useEffect } from "react";
import { apiClient, Ticket } from "@/lib/api";
import { toast } from "sonner";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_authenticated/student/tickets")({
  component: StudentTicketsComponent,
});

function StudentTicketsComponent() {
  // Core Grievance Incident Tracking States
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);

  // Modal Panel Visualization Control States
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [formSubmitting, setFormSubmitting] = useState<boolean>(false);

  // Form Field Input State Containers
  const [subject, setSubject] = useState("");
  const [category, setCategory] = useState("Finance & Accounts");
  const [priority, setPriority] = useState("Medium");
  const [description, setDescription] = useState("");

  // 🔄 Isolated Fetch Re-Trigger Conduit with Chronological Sorting Core
  const fetchUserGrievances = async (autoSelectFirst: boolean = false) => {
    try {
      const data = await apiClient.getTickets();

      // 👑 PRODUCTION SORT: Orders incoming items so fresh tickets populate the top of the timeline
      const sortedTickets = [...data].sort((a, b) => {
        const timeA = new Date(a.created_date || (a as any).created_at || 0).getTime();
        const timeB = new Date(b.created_date || (b as any).created_at || 0).getTime();
        return timeB - timeA;
      });

      setTickets(sortedTickets);

      if (sortedTickets.length > 0) {
        if (autoSelectFirst || !selectedTicket) {
          setSelectedTicket(sortedTickets[0]);
        } else {
          // Re-sync currently selected item metrics from refreshed array track
          const refreshedMatch = sortedTickets.find((t) => t.id === selectedTicket.id);
          if (refreshedMatch) setSelectedTicket(refreshedMatch);
        }
      }
    } catch (err) {
      console.error("Failed fetching tickets layer:", err);
      toast.error("Database connection fault: Unable to refresh incident ledger logs.");
    } finally {
      setLoading(false);
    }
  };

  // Syncs the UI grid with the background API thread on view mount
  useEffect(() => {
    fetchUserGrievances(true);
  }, []);

  // Structural Form Request Dispatch Handler
  const handleGrievanceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() || !description.trim()) return;

    setFormSubmitting(true);

    try {
      const success = await apiClient.createTicket(subject, category, priority, description);

      if (success) {
        toast.success("Grievance incident successfully logged and routed to department desk.");

        // Zero out field parameters safely
        setSubject("");
        setDescription("");
        setCategory("Finance & Accounts");
        setPriority("Medium");
        setIsModalOpen(false);

        // 🔄 Refresh table metrics to capture the database entry
        await fetchUserGrievances(true);
      }
    } catch (error) {
      toast.error("Submission blocked: Verification pipeline rejected data properties.");
    } finally {
      setFormSubmitting(false);
    }
  };

  const getStatusBadge = (status: string | undefined | null) => {
    const cleanStatus = status ? status.trim() : "Open";
    switch (cleanStatus) {
      case "Open":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 border border-rose-500/30 px-2.5 py-0.5 text-xs font-semibold text-rose-400 backdrop-blur-md shadow-[0_0_12px_rgba(244,63,94,0.1)]">
            <AlertCircle className="h-3 w-3" /> Open
          </span>
        );
      case "In Review":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 px-2.5 py-0.5 text-xs font-semibold text-amber-400 backdrop-blur-md shadow-[0_0_12px_rgba(245,158,11,0.1)]">
            <Clock className="h-3 w-3" /> In Review
          </span>
        );
      case "Resolved":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-0.5 text-xs font-semibold text-emerald-400 backdrop-blur-md shadow-[0_0_12px_rgba(16,185,129,0.1)]">
            <CheckCircle2 className="h-3 w-3" /> Resolved
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 border border-rose-500/30 px-2.5 py-0.5 text-xs font-semibold text-rose-400 backdrop-blur-md">
            <AlertCircle className="h-3 w-3" /> {cleanStatus}
          </span>
        );
    }
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] w-full px-4 py-6 text-white sm:px-6 lg:px-8 bg-[#020617]">
      <div className="mx-auto max-w-6xl">
        {/* Top Header Row */}
        <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center text-left">
          <div>
            <h1 className="font-display text-3xl font-bold tracking-tight">
              Support <span className="text-[color:var(--gold)]">Ticket Ledger</span>
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Monitor, track, and review active grievances and auto-escalated administrative
              requests.
            </p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center justify-center gap-2 rounded-xl bg-[color:var(--gold)] px-4 py-2.5 text-sm font-semibold text-slate-950 shadow-xl hover:bg-[color:var(--gold)]/90 transition-all border border-transparent active:scale-95 self-start sm:self-center"
          >
            <Plus className="h-4 w-4 stroke-[3]" /> File New Grievance
          </button>
        </div>

        {/* Dynamic Data Content Screen */}
        {loading ? (
          <div className="flex h-64 w-full flex-col items-center justify-center gap-2 text-slate-400">
            <Loader2 className="h-7 w-7 animate-spin text-[color:var(--gold)]" />
            <span className="text-sm font-medium tracking-wide">Assembling ledger records...</span>
          </div>
        ) : tickets.length === 0 ? (
          <div className="glass-panel rounded-2xl border border-white/10 bg-black/20 p-12 text-center">
            <AlertCircle className="mx-auto h-8 w-8 text-slate-500 mb-2" />
            <p className="text-sm text-slate-300">
              No grievance incidents recorded under this credential profile layer.
            </p>
          </div>
        ) : (
          /* Master-Detail Split Panel Layout */
          <div className="grid gap-6 lg:grid-cols-12 items-start">
            {/* Left Column: Tickets Master List Panel */}
            <div className="space-y-4 lg:col-span-5 max-h-[calc(100vh-15rem)] overflow-y-auto overflow-x-hidden px-3 py-2 pb-4 layout-scroll-container">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1 px-1 text-left">
                Your Incidents
              </p>
              {tickets.map((ticket) => {
                const displayDate = ticket.created_date || (ticket as any).created_at || "Recent";
                return (
                  <div
                    key={ticket.id}
                    onClick={() => setSelectedTicket(ticket)}
                    className={`glass-panel flex flex-col gap-3 rounded-xl border p-4 transition-all duration-300 ease-out cursor-pointer text-left select-none transform origin-center ${
                      selectedTicket?.id === ticket.id
                        ? "bg-[#002266]/90 border-[color:var(--gold)] shadow-md scale-[1.01]"
                        : "bg-[#001A4D]/25 border-white/5 hover:border-white/10 hover:bg-[#001A4D]/40 scale-100 shadow-none"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-xs font-bold text-slate-400">
                        {ticket.id}
                      </span>
                      {getStatusBadge(ticket.status)}
                    </div>
                    <h3 className="font-display text-sm font-bold leading-snug line-clamp-1 text-white">
                      {ticket.subject}
                    </h3>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-white/5">
                      <span
                        className={
                          selectedTicket?.id === ticket.id ? "text-slate-300" : "text-slate-400"
                        }
                      >
                        {ticket.category}
                      </span>
                      <span>{displayDate}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Right Column: Detailed Timeline Tracker */}
            <div className="lg:col-span-7">
              {selectedTicket ? (
                <div className="glass-panel sticky top-24 rounded-2xl border border-white/10 bg-[#001A4D]/40 p-6 backdrop-blur-lg shadow-2xl text-left">
                  {/* Meta details header banner */}
                  <div className="border-b border-white/10 pb-4 mb-5">
                    <div className="flex justify-between items-center flex-wrap gap-2 mb-2">
                      <span className="font-mono text-xs font-bold text-[color:var(--gold)] bg-white/5 border border-white/10 px-2 py-0.5 rounded-md">
                        {selectedTicket.id}
                      </span>
                      <div className="flex gap-2">
                        <span
                          className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded border ${
                            selectedTicket.priority === "Critical"
                              ? "bg-red-500/10 border-red-500/30 text-red-400"
                              : selectedTicket.priority === "High"
                                ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
                                : "bg-slate-500/10 border-slate-500/30 text-slate-400"
                          }`}
                        >
                          {selectedTicket.priority || "Medium"} Priority
                        </span>
                        {getStatusBadge(selectedTicket.status)}
                      </div>
                    </div>
                    <h2 className="font-display text-xl font-bold text-slate-100 leading-snug">
                      {selectedTicket.subject}
                    </h2>
                    <p className="text-xs text-slate-400 mt-1">
                      Category:{" "}
                      <span className="text-slate-300 font-medium">{selectedTicket.category}</span>{" "}
                      · Opened on{" "}
                      {selectedTicket.created_date ||
                        (selectedTicket as any).created_at ||
                        "Recent"}
                    </p>
                  </div>

                  {/* Description Frame */}
                  <div className="mb-6">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                      <FileText className="h-3.5 w-3.5 text-[color:var(--gold)]" /> Statement of
                      Grievance
                    </h4>
                    <p className="text-sm leading-relaxed text-slate-300 bg-white/5 p-4 rounded-xl border border-white/5 whitespace-pre-wrap">
                      {selectedTicket.description}
                    </p>
                  </div>

                  {/* Tracking Progress Timeline */}
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">
                      Lifecycle Audit Trail
                    </h4>
                    <div className="relative border-l-2 border-white/10 ml-2.5 pl-5 space-y-5">
                      {selectedTicket.timeline && selectedTicket.timeline.length > 0 ? (
                        selectedTicket.timeline.map((event, idx) => (
                          <div key={idx} className="relative">
                            <span
                              className={`absolute -left-[27px] top-0.5 flex h-3 w-3 rounded-full border-2 ${idx === 0 && selectedTicket.status !== "Resolved" ? "bg-[color:var(--gold)] border-slate-950 animate-pulse" : "bg-slate-600 border-slate-950"}`}
                            />
                            <span className="block text-[11px] font-medium text-slate-400">
                              {event.date || "Audit Tag"}
                            </span>
                            <p className="text-xs text-slate-200 mt-0.5 font-medium leading-relaxed">
                              {event.message}
                            </p>
                          </div>
                        ))
                      ) : (
                        <div className="relative">
                          <span className="absolute -left-[27px] top-0.5 flex h-3 w-3 rounded-full border-2 bg-[color:var(--gold)] border-slate-950" />
                          <span className="block text-[11px] font-medium text-slate-400">
                            System Log
                          </span>
                          <p className="text-xs text-slate-200 mt-0.5 font-medium leading-relaxed">
                            Ticket initiated successfully inside centralized repository maps.
                            Waiting for operational dispatch clearance.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="glass-panel flex h-48 flex-col items-center justify-center rounded-2xl border border-white/5 bg-[#001A4D]/20 text-slate-400 text-sm">
                  Select a ticket from the ledger overview pane to trace its administrative
                  fulfillment status.
                </div>
              )}
            </div>
          </div>
        )}

        {/* FLOATING DIALOG OVERLAY (THE MODAL) */}
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-md bg-black/60 transition-all animate-fade-in">
            <div className="glass-panel w-full max-w-xl rounded-2xl border border-white/10 bg-[#021333] p-6 shadow-2xl text-left space-y-4 relative">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-4 right-4 rounded-lg p-1.5 text-slate-400 hover:bg-white/5 hover:text-white transition-all"
              >
                <X className="h-4 w-4" />
              </button>

              <div className="flex items-center gap-2.5 border-b border-white/5 pb-3">
                <div className="rounded-lg bg-[color:var(--gold)]/10 border border-[color:var(--gold)]/20 p-2 text-[color:var(--gold)]">
                  <FileText className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">
                    Initialize Operational Grievance
                  </h3>
                  <p className="text-xs text-slate-400">
                    Direct transmission to formal systems administrators and dispatch coordinators
                  </p>
                </div>
              </div>

              <form onSubmit={handleGrievanceSubmit} className="space-y-4 pt-1">
                <div className="space-y-1.5">
                  <Label htmlFor="subject" className="text-xs text-slate-300">
                    Incident Descriptive Subject
                  </Label>
                  <Input
                    id="subject"
                    type="text"
                    required
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="e.g., UPI fee debited successfully but invoice reports balance due"
                    className="h-11 border-white/10 bg-black/40 text-white placeholder:text-slate-600 focus-visible:ring-[color:var(--gold)]/50"
                  />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-1.5">
                    <Label className="text-xs text-slate-300">
                      Institutional Department Classification
                    </Label>
                    {/* 👑 FIXED: Applied explicitly targeted bg and high-contrast text color overrides to form options to bypass browser dark theme locks */}
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full rounded-xl bg-[#0a122c] border border-white/10 p-3 text-sm text-slate-100 outline-none focus:border-[color:var(--gold)]/60 transition-colors cursor-pointer font-sans shadow-inner"
                    >
                      <option
                        value="Finance & Accounts"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Finance & Accounts
                      </option>
                      <option
                        value="Academic Operations"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Academic Operations
                      </option>
                      <option
                        value="Examinations Desk"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Examinations Desk
                      </option>
                      <option
                        value="Training & Placements (TPO)"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Training & Placements (TPO)
                      </option>
                      <option
                        value="IT Support & Campus Wi-Fi"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        IT Support & Campus Wi-Fi
                      </option>
                      <option
                        value="Hostel & Mess Management"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Hostel & Mess Management
                      </option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <Label className="text-xs text-slate-300">Initial Escalation Urgency</Label>
                    {/* 👑 FIXED: Injected explicit dark solid background styling classes directly into the urgency options to keep options crisp and readable */}
                    <select
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                      className="w-full rounded-xl bg-[#0a122c] border border-white/10 p-3 text-sm text-slate-100 outline-none focus:border-[color:var(--gold)]/60 transition-colors cursor-pointer font-sans shadow-inner"
                    >
                      <option
                        value="Low"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Low — General Request
                      </option>
                      <option
                        value="Medium"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Medium — Standard Issue
                      </option>
                      <option
                        value="High"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        High — Severe Bottleneck
                      </option>
                      <option
                        value="Critical"
                        className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                      >
                        Critical — Immediate Halt
                      </option>
                    </select>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="description" className="text-xs text-slate-300">
                    Problem Statement Specifications
                  </Label>
                  <textarea
                    id="description"
                    required
                    rows={4}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Provide granular log context, transactional references context, or structural statements here..."
                    className="w-full rounded-xl bg-black/30 border border-white/10 p-3 text-sm text-white placeholder-slate-500 outline-none focus:border-[color:var(--gold)]/60 transition-colors resize-none text-left"
                  />
                </div>

                <div className="pt-2 flex items-center justify-end gap-2.5">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="rounded-xl border border-white/5 bg-white/5 px-4 py-2.5 text-xs font-semibold hover:bg-white/10 text-slate-200 transition-all"
                  >
                    Cancel
                  </button>
                  <Button
                    type="submit"
                    disabled={formSubmitting}
                    className="bg-[color:var(--gold)] text-slate-950 font-bold px-5 h-10 rounded-xl hover:brightness-110"
                  >
                    {formSubmitting ? (
                      <>
                        <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> Filing Request...
                      </>
                    ) : (
                      "Deploy Ticket Matrix"
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
