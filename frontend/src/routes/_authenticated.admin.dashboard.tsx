import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ShieldCheck,
  Clock,
  CheckCircle2,
  Megaphone,
  ShieldAlert,
  Check,
  Loader2,
  FileUp,
  FileText,
  FileImage,
  FileSpreadsheet,
  FileCode,
  Layers,
  RefreshCw,
  UserPlus,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/lib/auth";
import { apiClient, Ticket, KBDocument } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/admin/dashboard")({
  component: AdminDashboardComponent,
});

function AdminDashboardComponent() {
  const { user } = useAuth();

  // 🎛️ Complete Admin Operational Hooks Stack
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [kbDocs, setKbDocs] = useState<KBDocument[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [kbLoading, setKbLoading] = useState<boolean>(true);
  const [rightPanelTab, setRightPanelTab] = useState<"notice" | "provision">("notice");

  const [noticeTitle, setNoticeTitle] = useState("");
  // 👑 FIXED: Sets standard initial state to first index matching production list categories
  const [noticeCategory, setNoticeCategory] = useState("Academics");
  const [noticeContent, setNoticeContent] = useState("");
  const [broadcastSuccess, setBroadcastSuccess] = useState(false);

  const [adminFullName, setAdminFullName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminUsername, setAdminUsername] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [provisionLoading, setProvisionLoading] = useState(false);

  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 📡 WEBSOCKET REAL-TIME SYNC MATRIX
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectionTimer: any = null;

    function connectWebSocketPipeline() {
      ws = new WebSocket("ws://127.0.0.1:8000/api/tickets/ws/live-sync");

      ws.onopen = () => {
        console.log("⚡ Real-time WebSockets synchronized cleanly with operational desk.");
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === "TICKET_CREATED") {
            const newTicket: Ticket = payload.data;
            setTickets((prev) => [newTicket, ...prev]);
            toast.success(
              `🎫 Alert: New ticket filed automatically from Student Hub: ${newTicket.id}`,
            );
          }
        } catch (err) {
          console.error("Error decoding server WebSocket serialized JSON buffer packet:", err);
        }
      };

      ws.onclose = () => {
        reconnectionTimer = setTimeout(connectWebSocketPipeline, 4000);
      };

      ws.onerror = () => {
        ws?.close();
      };
    }

    connectWebSocketPipeline();

    return () => {
      if (ws) ws.close();
      if (reconnectionTimer) clearTimeout(reconnectionTimer);
    };
  }, []);

  // Sync ticket and document streams on panel mount
  useEffect(() => {
    async function syncDashboardData() {
      try {
        const [ticketData, docData] = await Promise.all([
          apiClient.getTickets(),
          apiClient.getKBDocuments(),
        ]);
        setTickets(ticketData);
        setKbDocs(docData);
      } catch (err) {
        console.error("Failed syncing management operations cluster data:", err);
      } finally {
        setLoading(false);
        setKbLoading(false);
      }
    }
    syncDashboardData();
  }, []);

  // 🛡️ ADMINISTRATIVE clearance enforcement
  if (user?.role?.toLowerCase() !== "admin") {
    return (
      <div className="flex min-h-[calc(100vh-8rem)] w-full flex-col items-center justify-center p-6 text-center text-white">
        <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 p-8 backdrop-blur-xl shadow-2xl max-w-md">
          <ShieldAlert className="mx-auto h-12 w-12 text-rose-400 animate-bounce" />
          <h2 className="font-display mt-4 text-xl font-bold tracking-tight text-rose-100">
            Administrative Security Alert
          </h2>
          <p className="mt-2 text-xs leading-relaxed text-slate-300">
            Your current profile level does not possess active credentials required to look into
            this gateway terminal context.
          </p>
          <div className="mt-6">
            <Link
              to="/student/chat"
              className="inline-flex items-center justify-center rounded-xl bg-white/10 border border-white/10 px-5 py-2.5 text-xs font-semibold text-white hover:bg-white/15 transition-all"
            >
              ← Return to Chat Hub
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const refreshKnowledgeBase = async () => {
    setKbLoading(true);
    try {
      const serverFetchedDocs = await apiClient.getKBDocuments();
      setKbDocs(serverFetchedDocs);
    } catch (err) {
      console.error("Error manual indexing sync:", err);
    } finally {
      setKbLoading(false);
    }
  };

  const updateTicketStatus = async (id: string, nextStatus: string) => {
    setTickets((prev) => prev.map((t) => (t.id === id ? { ...t, status: nextStatus } : t)));
    try {
      await apiClient.updateTicketStatus(id, nextStatus);
      toast.success(`Ticket status updated to ${nextStatus}`);
    } catch (err) {
      toast.error("Failed to update status on server.");
    }
  };

  const handleNoticeBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noticeTitle || !noticeContent) return;
    try {
      const success = await apiClient.createNotice(noticeTitle, noticeCategory, noticeContent);
      if (success) {
        setBroadcastSuccess(true);
        toast.success("Official circular notice deployed across application feeds!");
        setTimeout(() => {
          setBroadcastSuccess(false);
          setNoticeTitle("");
          setNoticeContent("");
        }, 2000);
      }
    } catch (err) {
      toast.error("Notice broadcast pipeline execution failed.");
    }
  };

  const handleAdminProvisioning = async (e: React.FormEvent) => {
    e.preventDefault();
    const usernameRegex = /^[a-z][a-z0-9_.]{3,19}$/;
    if (!usernameRegex.test(adminUsername)) {
      toast.error(
        "Format Validation Failed: Usernames must start with a lowercase letter, contain only a-z, 0-9, underscores, or periods, and be between 4 and 20 characters.",
      );
      return;
    }
    setProvisionLoading(true);
    try {
      const response = await apiClient.createAdmin(
        adminFullName,
        adminEmail,
        adminUsername,
        adminPassword,
      );
      if (response.success) {
        toast.success(response.message || "Administrative operator profile deployed completely.");
        setAdminFullName("");
        setAdminEmail("");
        setAdminUsername("");
        setAdminPassword("");
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Failed to commit administrative account configuration.");
    } finally {
      setProvisionLoading(false);
    }
  };

  const processFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const targetedFile = files[0];
    setUploading(true);
    try {
      const completed = await apiClient.uploadKBDocument(targetedFile);
      if (completed) {
        toast.success("Document payload successfully dropped into ingestion pipeline.");
        refreshKnowledgeBase();
      }
    } catch (err) {
      console.error("Ingestion exception encountered:", err);
      toast.error("Document ingestion pipeline rejected data chunk files.");
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    processFileUpload(e.dataTransfer.files);
  };

  const getFileIcon = (format: string | undefined | null) => {
    if (!format) return <FileText className="h-3.5 w-3.5 shrink-0 text-slate-400" />;
    const fmt = format.toLowerCase();
    if (["png", "jpg", "jpeg", "webp", "svg", "bmp"].includes(fmt)) {
      return <FileImage className="h-3.5 w-3.5 shrink-0 text-purple-400" />;
    }
    if (["csv", "xlsx", "xls"].includes(fmt)) {
      return <FileSpreadsheet className="h-3.5 w-3.5 shrink-0 text-emerald-400" />;
    }
    if (["json", "html", "md", "xml", "js", "ts"].includes(fmt)) {
      return <FileCode className="h-3.5 w-3.5 shrink-0 text-amber-400" />;
    }
    return <FileText className="h-3.5 w-3.5 shrink-0 text-blue-400" />;
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] w-full px-4 py-6 text-white sm:px-6 lg:px-8 bg-[#020617]">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Terminal Header */}
        <div className="flex items-center gap-3 border-b border-white/10 pb-5">
          <div className="rounded-xl bg-amber-500/10 p-2.5 border border-amber-500/20 text-[color:var(--gold)] shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <ShieldCheck className="h-6 w-6 stroke-[2]" />
          </div>
          <div className="text-left">
            <h1 className="font-display text-2xl font-bold tracking-tight">
              Administrative <span className="text-[color:var(--gold)]">Control Terminal</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Systems Operations, Identity Provisioning & Campus Escalation Desk
            </p>
          </div>
        </div>

        {/* TOP ROW SPLIT: Incidents Queue & Multi-Tab Configuration Card Deck */}
        <div className="grid gap-6 lg:grid-cols-12 items-stretch">
          {/* LEFT: Live Incident Action Desk */}
          <div className="space-y-4 lg:col-span-7">
            <div className="glass-panel rounded-2xl border border-white/10 bg-[#001A4D]/40 p-5 backdrop-blur-md shadow-xl h-full flex flex-col justify-between">
              <div>
                <h2 className="font-display text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
                  <span className="flex h-2 w-2 rounded-full bg-rose-500 animate-ping" />
                  Pending Grievance Dispatch Queue
                </h2>

                {loading ? (
                  <div className="flex h-48 w-full flex-col items-center justify-center gap-2 text-slate-400">
                    <Loader2 className="h-6 w-6 animate-spin text-[color:var(--gold)]" />
                    <span className="text-xs font-medium tracking-wide">
                      Syncing incident records...
                    </span>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1 layout-scroll-container">
                    {tickets.map((ticket) => (
                      <div
                        key={ticket.id}
                        className="rounded-xl border border-white/5 bg-black/20 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in"
                      >
                        <div className="space-y-1 text-left max-w-sm sm:max-w-md">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-mono text-xs font-bold text-slate-400">
                              {ticket.id}
                            </span>
                            <span className="text-[10px] uppercase font-bold text-slate-300 font-mono tracking-wider bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                              {ticket.category}
                            </span>
                            {ticket.status === "Open" ? (
                              <span className="text-[10px] uppercase font-bold text-rose-400 font-mono tracking-wider bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20">
                                Open
                              </span>
                            ) : ticket.status === "In Review" ? (
                              <span className="text-[10px] uppercase font-bold text-amber-400 font-mono tracking-wider bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
                                In Review
                              </span>
                            ) : (
                              <span className="text-[10px] uppercase font-bold text-emerald-400 font-mono tracking-wider bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                                Resolved
                              </span>
                            )}
                          </div>
                          <h3 className="text-sm font-bold text-slate-200 leading-snug line-clamp-1">
                            {ticket.subject}
                          </h3>
                          <p className="text-xs text-slate-400">
                            Opened trace:{" "}
                            <span className="text-slate-300 font-medium">
                              {ticket.created_date || (ticket as any).created_at}
                            </span>
                          </p>
                        </div>

                        <div className="flex items-center gap-1.5 self-end sm:self-center">
                          <button
                            onClick={() => updateTicketStatus(ticket.id, "In Review")}
                            className={`rounded-lg p-2 text-xs font-medium border transition-all flex items-center gap-1 ${ticket.status === "In Review" ? "bg-amber-500/20 border-amber-500/40 text-amber-400 shadow-md" : "bg-white/5 border-white/5 text-slate-400 hover:bg-white/10"}`}
                            title="Mark In Review"
                          >
                            <Clock className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => updateTicketStatus(ticket.id, "Resolved")}
                            className={`rounded-lg p-2 text-xs font-medium border transition-all flex items-center gap-1 ${ticket.status === "Resolved" ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400 shadow-md" : "bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-emerald-400"}`}
                            title="Mark Resolved"
                          >
                            <CheckCircle2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* RIGHT: Operational Card Deck Form Router Container */}
          <div className="lg:col-span-5">
            <div className="glass-panel rounded-2xl border border-white/10 bg-[#001A4D]/40 p-5 backdrop-blur-md shadow-xl text-left h-full flex flex-col justify-between">
              <div className="grid grid-cols-2 gap-1 rounded-xl bg-black/40 p-1 border border-white/5 mb-4 shrink-0">
                <button
                  type="button"
                  onClick={() => setRightPanelTab("notice")}
                  className={`flex items-center justify-center gap-1.5 rounded-lg py-2 text-xs font-bold transition-all ${rightPanelTab === "notice" ? "bg-[color:var(--gold)] text-slate-950 shadow-md" : "text-slate-400 hover:text-white"}`}
                >
                  <Megaphone className="h-3.5 w-3.5" /> Broadcast
                </button>
                <button
                  type="button"
                  onClick={() => setRightPanelTab("provision")}
                  className={`flex items-center justify-center gap-1.5 rounded-lg py-2 text-xs font-bold transition-all ${rightPanelTab === "provision" ? "bg-[color:var(--gold)] text-slate-950 shadow-md" : "text-slate-400 hover:text-white"}`}
                >
                  <UserPlus className="h-3.5 w-3.5" /> Add Admin
                </button>
              </div>

              {rightPanelTab === "notice" && (
                <form
                  onSubmit={handleNoticeBroadcast}
                  className="space-y-4 flex-1 flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-slate-300">
                        Announcement Title
                      </label>
                      <input
                        type="text"
                        value={noticeTitle}
                        onChange={(e) => setNoticeTitle(e.target.value)}
                        placeholder="e.g., Extended Lab Timings for Hackathon Prep"
                        className="w-full rounded-xl bg-black/20 border border-white/10 p-3 text-sm text-white placeholder-slate-500 outline-none focus:border-[color:var(--gold)]/60 transition-colors"
                        required
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-slate-300">Category Tag</label>
                      {/* 👑 FIXED: Applied clear background and visible colors directly onto select element & option trees to block browser defaults rendering dark tags */}
                      <select
                        value={noticeCategory}
                        onChange={(e) => setNoticeCategory(e.target.value)}
                        className="w-full rounded-xl bg-[#0a122c] border border-white/10 p-3 text-sm text-slate-100 outline-none focus:border-[color:var(--gold)]/60 transition-colors cursor-pointer font-sans shadow-inner"
                      >
                        {/* 👑 ENHANCED CATEGORIES MATRIX: Expands choices completely to support real production operations criteria parameters */}
                        <option
                          value="Academics"
                          className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                        >
                          Academics
                        </option>
                        <option
                          value="Examinations"
                          className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                        >
                          Examinations
                        </option>
                        <option
                          value="Placements"
                          className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                        >
                          Placements & Career
                        </option>
                        <option
                          value="Events"
                          className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                        >
                          Events & Hackathons
                        </option>
                        <option
                          value="Finance"
                          className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                        >
                          Finance & Scholarships
                        </option>
                        <option
                          value="Facilities"
                          className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                        >
                          Hostel & Infrastructure
                        </option>
                        <option
                          value="Admin"
                          className="bg-[#0b1430] text-slate-100 font-semibold py-2"
                        >
                          General Administration
                        </option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-slate-300">
                        Detailed Circular Content
                      </label>
                      <textarea
                        rows={3}
                        value={noticeContent}
                        onChange={(e) => setNoticeContent(e.target.value)}
                        placeholder="Type formal declaration statements or structural steps here..."
                        className="w-full rounded-xl bg-black/20 border border-white/10 p-3 text-sm text-white placeholder-slate-500 outline-none focus:border-[color:var(--gold)]/60 transition-colors resize-none"
                        required
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={broadcastSuccess}
                    className={`w-full font-bold text-xs rounded-xl py-3 border transition-all mt-4 flex items-center justify-center gap-2 ${broadcastSuccess ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400 shadow-md" : "bg-[color:var(--gold)] border-transparent text-slate-950 hover:brightness-110"}`}
                  >
                    {broadcastSuccess ? (
                      <>
                        <Check className="h-4 w-4 stroke-[3]" /> Broadcast Deployed!
                      </>
                    ) : (
                      <>
                        <Megaphone className="h-4 w-4" /> Transmit Live Notice
                      </>
                    )}
                  </button>
                </form>
              )}

              {rightPanelTab === "provision" && (
                <form
                  onSubmit={handleAdminProvisioning}
                  className="space-y-3 flex-1 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div>
                      <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                        Full Operator Name
                      </label>
                      <input
                        type="text"
                        value={adminFullName}
                        onChange={(e) => setAdminFullName(e.target.value)}
                        placeholder="Dean Academic Operations"
                        className="w-full rounded-xl bg-black/20 border border-white/10 p-2.5 text-xs text-white placeholder-slate-600 outline-none focus:border-[color:var(--gold)]/60 transition-colors"
                        required
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                        Institutional Email Address
                      </label>
                      <input
                        type="email"
                        value={adminEmail}
                        onChange={(e) => setAdminEmail(e.target.value)}
                        placeholder="dean.ops@amity.edu"
                        className="w-full rounded-xl bg-black/20 border border-white/10 p-2.5 text-xs text-white placeholder-slate-600 outline-none focus:border-[color:var(--gold)]/60 transition-colors"
                        required
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                        Unique Security Username
                      </label>
                      <input
                        type="text"
                        value={adminUsername}
                        onChange={(e) => setAdminUsername(e.target.value)}
                        placeholder="dean_ops"
                        className="w-full rounded-xl bg-black/20 border border-white/10 p-2.5 text-xs text-white placeholder-slate-600 outline-none focus:border-[color:var(--gold)]/60 transition-colors"
                        required
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                        Temporary Access Key Pass
                      </label>
                      <input
                        type="password"
                        value={adminPassword}
                        onChange={(e) => setAdminPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full rounded-xl bg-black/20 border border-white/10 p-2.5 text-xs text-white placeholder-slate-600 outline-none focus:border-[color:var(--gold)]/60 transition-colors"
                        required
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={provisionLoading}
                    className="w-full font-bold text-xs rounded-xl py-3 border border-transparent mt-4 bg-[color:var(--gold)] text-slate-950 hover:brightness-110 flex items-center justify-center gap-2 transition-all shadow-md active:scale-[0.98]"
                  >
                    {provisionLoading ? (
                      <>
                        <Loader2 className="h-3.5 w-3.5 animate-spin" /> Provisioning Credentials...
                      </>
                    ) : (
                      <>
                        <UserPlus className="h-3.5 w-3.5" /> Deploy System Profile
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>

        {/* 📂 LOWER SECTION: Knowledge Base Management Table Array */}
        <div className="glass-panel rounded-2xl border border-white/10 bg-[#001A4D]/40 p-5 backdrop-blur-md shadow-xl text-left">
          <div className="mb-4 flex items-center justify-between border-b border-white/5 pb-3">
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-[color:var(--gold)]" />
              <div>
                <h2 className="font-display text-base font-bold text-slate-100">
                  Helpdesk AI Knowledge Base Ingestion
                </h2>
                <p className="text-xs text-slate-400">
                  Stream document binaries natively to feed vector index clusters
                </p>
              </div>
            </div>
            <button
              onClick={refreshKnowledgeBase}
              className="rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-[color:var(--gold)] border border-white/5 bg-white/5 transition-all"
            >
              <RefreshCw
                className={`h-4 w-4 ${kbLoading ? "animate-spin text-[color:var(--gold)]" : ""}`}
              />
            </button>
          </div>

          <div className="grid gap-6 lg:grid-cols-12">
            <div className="lg:col-span-5">
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`relative flex h-full min-h-[12rem] flex-col items-center justify-center rounded-2xl border-2 border-dashed p-6 text-center transition-all cursor-pointer select-none ${isDragging ? "border-[color:var(--gold)] bg-amber-500/10 shadow-[0_0_20px_rgba(245,158,11,0.1)]" : "border-white/20 bg-black/20 hover:border-white/40"}`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => processFileUpload(e.target.files)}
                  className="hidden"
                />
                {uploading ? (
                  <div className="space-y-2 pointer-events-none">
                    <Loader2 className="mx-auto h-8 w-8 animate-spin text-[color:var(--gold)]" />
                    <p className="text-xs font-semibold text-slate-200">
                      Streaming payload to tokenizer pipeline...
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2 pointer-events-none">
                    <div className="mx-auto grid h-10 w-10 place-items-center rounded-xl bg-white/5 border border-white/10 text-[color:var(--gold)] shadow-inner">
                      <FileUp className="h-5 w-5" />
                    </div>
                    <p className="text-xs font-semibold text-slate-200">
                      Drag & drop campus asset here
                    </p>
                    <p className="mt-0.5 text-[11px] text-slate-400">
                      or click to browse local storage directory
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:col-span-7 flex flex-col justify-between">
              <div className="rounded-xl border border-white/5 bg-black/10 overflow-hidden">
                <div className="max-h-[12rem] overflow-y-auto pr-1 layout-scroll-container">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-white/10 bg-white/5 text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                        <th className="p-2.5">Asset Reference</th>
                        <th className="p-2.5">Format</th>
                        <th className="p-2.5">Vector Status</th>
                        <th className="p-3 text-right">Size</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-xs text-slate-300">
                      {kbDocs.length === 0 ? (
                        <tr>
                          <td colSpan={4} className="p-6 text-center text-slate-500 font-medium">
                            No external campus guidelines indexed. Cluster registry empty.
                          </td>
                        </tr>
                      ) : (
                        kbDocs.map((doc) => (
                          <tr key={doc.id} className="hover:bg-white/5 transition-colors">
                            <td className="p-2.5 max-w-xs font-medium text-slate-200 flex items-center gap-2 truncate">
                              {getFileIcon(
                                doc.format || (doc as any).type || (doc as any).extension,
                              )}
                              <span className="truncate">{doc.filename}</span>
                            </td>
                            <td className="p-2.5 font-mono text-[10px] text-slate-400 font-bold">
                              {doc.format || (doc as any).type || "pdf"}
                            </td>
                            <td className="p-2.5">
                              <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 text-[10px] font-medium text-emerald-400 font-mono">
                                Indexed
                              </span>
                            </td>
                            <td className="p-2.5 text-right font-mono text-[10px] text-slate-400">
                              {doc.fileSize || (doc as any).size || "0 KB"}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
              <p className="text-[11px] text-slate-400 mt-2 px-1 leading-normal">
                ⚠️ Vector tokens are updated live on local storage mediums.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
