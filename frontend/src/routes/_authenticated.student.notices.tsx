import { createFileRoute } from "@tanstack/react-router";
import {
  Megaphone,
  Calendar,
  Tag,
  Search,
  Bell,
  Loader2,
  BookOpen,
  ArrowRight,
} from "lucide-react";
import { useState, useEffect } from "react";
import { apiClient, Notice } from "@/lib/api";

export const Route = createFileRoute("/_authenticated/student/notices")({
  component: StudentNoticesComponent,
});

function StudentNoticesComponent() {
  // Core Notice Stream States
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedNotice, setSelectedNotice] = useState<Notice | null>(null);

  // Search & Filter Coordination States
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeCategory, setActiveCategory] = useState<string>("All");

  // 🏫 ENTERPRISE-GRADE BROADCAST CATEGORIES
  const categories = [
    "All",
    "Academics",
    "Examinations",
    "Placements",
    "Events",
    "Finance",
    "Facilities",
    "Admin",
  ];

  // Fetch broadcast stream from centralized API routing layer
  useEffect(() => {
    async function fetchCampusAnnouncements() {
      try {
        const data = await apiClient.getNotices();
        setNotices(data);
        if (data && data.length > 0) {
          setSelectedNotice(data[0]); // Default focus on the latest official declaration
        }
      } catch (err) {
        console.error("Failed connecting to circular announcement nodes:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchCampusAnnouncements();
  }, []);

  // Filter Pipeline: Handles real-time search queries and category tags simultaneously
  const filteredNotices = notices.filter((notice) => {
    const matchesCategory =
      activeCategory === "All" || notice.category.toLowerCase() === activeCategory.toLowerCase();
    const matchesSearch =
      notice.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      notice.content.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // 🎨 Contextual Production Color Matrix Mapper
  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case "academics":
        return "text-blue-400 bg-blue-500/10 border-blue-500/20";
      case "examinations":
        return "text-rose-400 bg-rose-500/10 border-rose-500/20";
      case "placements":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "events":
        return "text-purple-400 bg-purple-500/10 border-purple-500/20";
      case "finance":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      case "facilities":
        return "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";
      case "admin":
        return "text-fuchsia-400 bg-fuchsia-500/10 border-fuchsia-500/20";
      default:
        return "text-slate-400 bg-slate-500/10 border-slate-500/20";
    }
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] w-full px-4 py-6 text-white sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        {/* Workspace Title Header Section */}
        <div className="mb-6 border-b border-white/10 pb-5 text-left">
          <div className="flex items-center gap-2.5">
            <div className="rounded-xl bg-blue-500/10 p-2 border border-blue-500/20 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
              <Bell className="h-5 w-5" />
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold tracking-tight">
                Campus <span className="text-[color:var(--gold)]">Bulletin Board</span>
              </h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Verified administrative broadcasts, timeline notifications, and systemic circulars.
              </p>
            </div>
          </div>
        </div>

        {/* 🔍 FILTER MATRIX BAR: Interactive Search Input & Category Tags */}
        <div className="mb-6 flex flex-col xl:flex-row xl:items-center justify-between gap-4 bg-black/20 border border-white/5 p-4 rounded-2xl backdrop-blur-md">
          {/* Real-time Input Indexer */}
          <div className="relative flex-1 w-full xl:max-w-md">
            <Search className="absolute top-3.5 left-4 h-4 w-4 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search declarations, exam patterns, schedules..."
              className="w-full rounded-xl bg-black/30 border border-white/10 pl-11 pr-4 py-3 text-sm text-white placeholder-slate-500 outline-none focus:border-blue-500/50 transition-colors"
            />
          </div>

          {/* Expanded Production Filtering Chips Stack */}
          <div className="flex flex-wrap items-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  setActiveCategory(cat);
                  setSelectedNotice(null);
                }}
                className={`rounded-xl px-3.5 py-2 text-xs font-semibold tracking-wide border transition-all ${
                  activeCategory === cat
                    ? "bg-[color:var(--gold)] border-[color:var(--gold)]/20 text-slate-950 font-bold shadow-md shadow-amber-500/5"
                    : "bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-white"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Master System Content Interface Grid */}
        {loading ? (
          <div className="flex h-64 w-full flex-col items-center justify-center gap-2 text-slate-400">
            <Loader2 className="h-7 w-7 animate-spin text-[color:var(--gold)]" />
            <span className="text-sm font-medium tracking-wide">
              Querying live board distributions...
            </span>
          </div>
        ) : filteredNotices.length === 0 ? (
          <div className="glass-panel rounded-2xl border border-white/10 bg-black/20 p-12 text-center">
            <Megaphone className="mx-auto h-8 w-8 text-slate-600 mb-2" />
            <p className="text-sm text-slate-400">
              No active circulars match your current filter preferences criteria.
            </p>
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-12 items-start">
            {/* LEFT COLUMN: Broadcast Circular Cards Stream (5 Columns) */}
            {/* 🛡️ FIX: Applied overflow-x-hidden paired with strict padding buffers (px-3 py-2) to fully protect edges */}
            <div className="space-y-4 lg:col-span-5 max-h-[calc(100vh-19rem)] overflow-y-auto overflow-x-hidden px-3 py-2 pb-4 layout-scroll-container">
              {filteredNotices.map((notice) => (
                <div
                  key={notice.id}
                  onClick={() => setSelectedNotice(notice)}
                  className={`glass-panel flex flex-col gap-3 rounded-2xl border p-5 transition-all duration-300 ease-out cursor-pointer text-left select-none transform origin-center ${
                    selectedNotice?.id === notice.id
                      ? "bg-[#002266]/90 border-blue-500/50 shadow-[0_0_25px_rgba(59,130,246,0.15)] scale-[1.025] ring-1 ring-blue-400/20"
                      : "bg-[#001A4D]/25 border-white/5 hover:border-white/10 hover:bg-[#001A4D]/40 scale-100 shadow-none"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded border font-mono ${getCategoryColor(notice.category)}`}
                    >
                      {notice.category}
                    </span>
                    <span className="flex items-center gap-1 text-[11px] text-slate-400 font-medium">
                      <Calendar className="h-3 w-3" />
                      {notice.date}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <h3
                      className={`font-display text-base font-bold leading-snug line-clamp-2 transition-colors ${
                        selectedNotice?.id === notice.id ? "text-white" : "text-slate-100"
                      }`}
                    >
                      {notice.title}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                      {notice.excerpt}
                    </p>
                  </div>

                  <div className="flex items-center justify-end text-[11px] font-bold text-blue-400 pt-2 border-t border-white/5 group">
                    <span className="flex items-center gap-1 group-hover:text-blue-300 transition-colors">
                      Expand Full Circular
                      <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* RIGHT COLUMN: Interactive Deep Reading Document Vault Container (7 Columns) */}
            <div className="lg:col-span-7">
              {selectedNotice ? (
                <div className="glass-panel sticky top-24 rounded-2xl border border-white/10 bg-[#001A4D]/40 p-6 backdrop-blur-lg shadow-2xl text-left space-y-5">
                  {/* Detailed Meta Header Banner */}
                  <div className="border-b border-white/10 pb-4 space-y-3">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded border font-mono ${getCategoryColor(selectedNotice.category)}`}
                      >
                        {selectedNotice.category}
                      </span>
                      <span className="flex items-center gap-1 text-xs text-slate-400 font-medium">
                        <Calendar className="h-3.5 w-3.5" />
                        Published Timeline: {selectedNotice.date}
                      </span>
                    </div>
                    <h2 className="font-display text-2xl font-bold text-slate-100 leading-snug">
                      {selectedNotice.title}
                    </h2>
                  </div>

                  {/* Formal Declaration Document Box Body */}
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <BookOpen className="h-4 w-4 text-[color:var(--gold)]" />
                      Official Circular Payload Statements
                    </h4>
                    <div className="text-sm leading-relaxed text-slate-200 bg-black/40 p-5 rounded-2xl border border-white/5 whitespace-pre-wrap font-sans shadow-inner">
                      {selectedNotice.content}
                    </div>
                  </div>

                  {/* Corporate Disclaimer Footnote */}
                  <div className="rounded-xl bg-white/5 border border-white/5 p-3.5 text-[11px] text-slate-400 leading-normal flex gap-2">
                    <Tag className="h-4 w-4 text-blue-400 shrink-0 mt-0.5" />
                    <p>
                      This transmission constitutes a formal institutional declaration dispatched
                      directly from the Office of Administration. Retained vector tokens are
                      permanently indexed for automated cross-referencing nodes inside the Helpdesk
                      AI core.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="glass-panel flex h-48 flex-col items-center justify-center rounded-2xl border border-white/5 bg-[#001A4D]/20 text-slate-400 text-sm">
                  Select an administrative notification from the bulletin feed ledger to expand
                  structural logs.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
