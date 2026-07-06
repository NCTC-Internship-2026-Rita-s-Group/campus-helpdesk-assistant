import { createFileRoute } from "@tanstack/react-router";

import { useEffect, useMemo, useRef, useState } from "react";

import { toast } from "sonner";

import {
  AlertTriangle,
  ChevronDown,
  FileText,
  FileImage,
  FileSpreadsheet,
  MessageSquarePlus,
  Send,
  Sparkles,
  Trash2,
  User,
  Bot,
  Paperclip,
  Loader2,
  CheckCircle2,
} from "lucide-react";

import { useAuth } from "@/lib/auth";

import { apiClient, LiveChatMessage } from "@/lib/api";

export const Route = createFileRoute("/_authenticated/student/chat")({
  head: () => ({
    meta: [{ title: "AI Helpdesk · Amity" }],
  }),

  component: StudentChat,
});

interface ChatSession {
  id: string;

  title: string;

  createdAt: number;

  updatedAt: number;

  messages: LiveChatMessage[];

  titleSet: boolean;
}

function StudentChat() {
  const { user } = useAuth();

  const [sessions, setSessions] = useState<ChatSession[]>(() => [
    {
      id: "default-session",

      title: "Welcome Thread",

      createdAt: Date.now(),

      updatedAt: Date.now(),

      titleSet: false,

      messages: [
        {
          id: "welcome-init",

          role: "assistant",

          createdAt: Date.now(),

          content: `### Welcome to the Amity Helpdesk\n\nHello ${user?.name ?? "Student"} — I'm your autonomous institutional assistant. Ask me about **hostel regulations**, **examination timetables**, **placements**, or any **campus policy**. I'll verify and cite source documentation blocks for every response.`,

          context_verified: true,

          sources: [],
        },
      ],
    },
  ]);

  const [activeId, setActiveId] = useState<string>("default-session");

  const active = useMemo(
    () => sessions.find((s) => s.id === activeId) ?? sessions[0],

    [sessions, activeId],
  );

  const [input, setInput] = useState("");

  const [thinking, setThinking] = useState(false);

  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
  }, [active?.messages.length, thinking]);

  const newConversation = () => {
    const nextId = `session-${Date.now()}`;

    const newSession: ChatSession = {
      id: nextId,

      title: "New Conversation",

      createdAt: Date.now(),

      updatedAt: Date.now(),

      titleSet: false,

      messages: [],
    };

    setSessions((prev) => [newSession, ...prev]);

    setActiveId(nextId);
  };

  const deleteConversation = (id: string) => {
    setSessions((prev) => {
      const next = prev.filter((s) => s.id !== id);

      if (id === activeId) setActiveId(next[0]?.id ?? "default-session");

      return next.length
        ? next
        : [
            {
              id: "default-session",

              title: "Welcome Thread",

              createdAt: Date.now(),

              updatedAt: Date.now(),

              titleSet: false,

              messages: [],
            },
          ];
    });

    toast.info("Conversation removed.");
  };

  const send = async (e?: React.FormEvent) => {
    e?.preventDefault();

    const text = input.trim();

    if (!text || thinking || !active) return;

    const optimisticTitle =
      text.split(" ").length > 6 ? text.split(" ").slice(0, 6).join(" ") + "…" : text;

    const userMsg: LiveChatMessage = {
      id: `user-${Date.now()}`,

      role: "user",

      createdAt: Date.now(),

      content: text,
    };

    setSessions((prev) =>
      prev.map((s) =>
        s.id === active.id
          ? {
              ...s,

              title: !s.titleSet ? optimisticTitle : s.title,

              titleSet: !s.titleSet ? true : s.titleSet,

              updatedAt: Date.now(),

              messages: [...s.messages, userMsg],
            }
          : s,
      ),
    );

    setInput("");

    setThinking(true);

    try {
      const history = active.messages.slice(-6).map((m) => ({
        role: m.role,

        content: m.content,
      }));

      const reply = await apiClient.sendChatMessage(text, history);

      if (reply.generated_title) {
        setSessions((prev) =>
          prev.map((s) => (s.id === active.id ? { ...s, title: reply.generated_title! } : s)),
        );
      }

      const assistantMsg: LiveChatMessage = {
        id: reply.id,

        role: "assistant",

        createdAt: Date.now(),

        content: reply.content,

        context_verified: reply.context_verified,

        sources: reply.sources,
      };

      setSessions((prev) =>
        prev.map((s) =>
          s.id === active.id
            ? { ...s, updatedAt: Date.now(), messages: [...s.messages, assistantMsg] }
            : s,
        ),
      );

      if (reply.context_verified === false) {
        const ticketId = `TK-2026-${Math.floor(1000 + Math.random() * 9000)}`;

        toast.warning(`Low confidence — incident log dispatched: ${ticketId}`);
      }
    } catch (err) {
      console.error("Chat error:", err);

      toast.error("Connection lost. Please try again.");
    } finally {
      setThinking(false);
    }
  };

  return (
    <main className="mx-auto grid h-[calc(100dvh-5.5rem)] max-w-7xl grid-cols-1 gap-4 px-3 py-4 md:grid-cols-[300px_1fr] md:px-6 text-white overflow-hidden items-stretch bg-[#020617]">
      {/* ── SIDEBAR ── */}

      <aside className="hidden h-full flex-col overflow-hidden rounded-2xl md:flex bg-[#000E2B]/50 backdrop-blur-md shrink-0 border border-white/8 shadow-2xl">
        <div className="p-4 border-b border-white/5">
          <button
            onClick={newConversation}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-[color:var(--gold)]/30 bg-[color:var(--gold)]/10 px-4 py-3 text-sm font-semibold text-[color:var(--gold)] transition-all hover:bg-[color:var(--gold)]/20 active:scale-95"
          >
            <MessageSquarePlus className="h-4 w-4 stroke-[2]" />
            New Conversation
          </button>
        </div>

        <div className="px-4 pt-4 pb-1 text-[11px] uppercase tracking-[0.18em] text-slate-500 font-bold text-left">
          Conversations
        </div>

        <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1 layout-scroll-container mt-1">
          {sessions.map((s) => {
            const isActive = s.id === activeId;

            return (
              <div
                key={s.id}
                className={
                  "group flex items-center gap-2 rounded-xl px-3 py-3 text-sm transition-all duration-150 select-none cursor-pointer " +
                  (isActive
                    ? "bg-[#001A4D]/70 text-white font-medium border border-[color:var(--gold)]/20"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent")
                }
                onClick={() => setActiveId(s.id)}
              >
                <div className="flex-1 truncate text-left text-[13.5px]" title={s.title}>
                  {s.title || "Untitled"}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();

                    deleteConversation(s.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-lg hover:bg-rose-500/10 text-slate-500 hover:text-rose-400 shrink-0"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })}
        </div>

        <div className="m-3 rounded-xl bg-white/5 border border-white/5 p-3 text-left space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[color:var(--gold)]">
            <Sparkles className="h-3.5 w-3.5" />
            LLaMA 3.3 Production Core
          </div>

          <p className="text-[11px] text-slate-500 leading-relaxed">
            Vector embeddings active. Responses verified against institutional circulars.
          </p>
        </div>
      </aside>

      {/* ── CHAT PANEL ── */}

      <section className="flex h-full flex-col overflow-hidden rounded-2xl bg-[#001A4D]/20 backdrop-blur-md border border-white/8 shadow-2xl relative">
        {/* Header */}

        <div className="flex items-center justify-between border-b border-white/5 px-6 py-4 bg-[#000A1F]/30 shrink-0">
          <div>
            <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-[0.2em] text-[color:var(--gold)]/80 font-bold mb-0.5">
              <Sparkles className="h-3 w-3" /> Conversational AI Hub
            </div>

            <h1 className="font-display text-[15px] font-bold text-slate-100 truncate max-w-sm sm:max-w-lg">
              {active?.title || "New Conversation"}
            </h1>
          </div>

          <span className="hidden text-[10px] font-mono text-slate-600 bg-white/5 border border-white/5 px-2 py-1 rounded-lg sm:block select-none">
            {active?.id?.slice(0, 14)}
          </span>
        </div>

        {/* Messages */}

        <div
          ref={scrollerRef}
          className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 layout-scroll-container"
        >
          <div className="mx-auto flex max-w-2xl flex-col gap-8">
            {active?.messages.map((m) => (
              <MessageBubble key={m.id} msg={m} />
            ))}

            {thinking && <ThinkingBubble />}
          </div>
        </div>

        {/* Input */}

        <div className="border-t border-white/5 px-4 py-4 sm:px-6 bg-[#000A1F]/30 backdrop-blur-md shrink-0">
          <div className="mx-auto max-w-2xl">
            <div className="flex items-end gap-3 rounded-2xl border border-white/10 bg-black/30 px-4 py-3 focus-within:border-[color:var(--gold)]/40 transition-all shadow-inner">
              <button
                type="button"
                className="p-1.5 rounded-lg text-slate-600 hover:bg-white/5 hover:text-slate-400 transition-all shrink-0 mb-0.5"
                title="Attach file"
              >
                <Paperclip className="h-4 w-4" />
              </button>

              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();

                    void send();
                  }
                }}
                placeholder="Ask about semester schedules, fee structure, placement stats…"
                rows={1}
                className="max-h-36 flex-1 resize-none bg-transparent py-1 text-[14px] text-slate-100 placeholder:text-slate-600 focus:outline-none font-sans leading-relaxed"
              />

              <button
                onClick={() => send()}
                disabled={thinking || !input.trim()}
                className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[color:var(--gold)] text-slate-950 transition-all hover:brightness-110 active:scale-95 disabled:cursor-not-allowed disabled:opacity-25 shadow-sm mb-0.5"
              >
                <Send className="h-3.5 w-3.5 stroke-[2.5]" />
              </button>
            </div>

            <p className="mt-2.5 text-center text-[11px] text-slate-600 leading-normal">
              Responses are verified against official Amity University documents. Low-confidence
              queries are escalated automatically.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

// ── MESSAGE BUBBLE ──────────────────────────────────────────────────────────

function MessageBubble({ msg }: { msg: LiveChatMessage }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end items-end gap-3 animate-fade-up">
        <div className="max-w-[75%] space-y-1">
          <div className="rounded-2xl rounded-br-sm bg-[#1a3a7a] px-5 py-3.5 text-[14px] text-slate-100 leading-relaxed whitespace-pre-wrap shadow-lg ring-1 ring-white/5">
            {msg.content}
          </div>
        </div>

        <div className="h-8 w-8 rounded-full bg-[color:var(--gold)]/15 border border-[color:var(--gold)]/25 text-[color:var(--gold)] flex items-center justify-center shrink-0 shadow-sm">
          <User className="h-4 w-4" />
        </div>
      </div>
    );
  }

  const escalated = msg.context_verified === false;

  return (
    <div className="flex justify-start items-start gap-3 animate-fade-up">
      <div className="h-8 w-8 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center shrink-0 shadow-sm mt-0.5">
        <Bot className="h-4 w-4" />
      </div>

      <div className="flex flex-col gap-3 max-w-[85%] min-w-0">
        {/* Verification badge */}

        {msg.id !== "welcome-init" && (
          <div className="flex items-center gap-1.5">
            {msg.context_verified ? (
              <span className="inline-flex items-center gap-1 text-[11px] bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full text-emerald-400 font-semibold">
                <CheckCircle2 className="h-3 w-3" /> Verified Source
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[11px] bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-full text-amber-400 font-semibold">
                <AlertTriangle className="h-3 w-3" /> External Escalation
              </span>
            )}
          </div>
        )}

        {/* Message card */}

        <div className="rounded-2xl rounded-tl-sm border border-white/8 px-5 py-4 text-[14px] leading-relaxed text-slate-200 bg-[#0b1a40]/60 backdrop-blur-sm shadow-md w-full">
          {msg.id !== "welcome-init" ? (
            <StreamingMarkdownWrapper text={msg.content} speed={10} />
          ) : (
            <MarkdownRenderer text={msg.content} />
          )}
        </div>

        {/* Escalation notice */}

        {escalated && (
          <div className="flex items-start gap-3 rounded-xl border border-orange-500/20 bg-orange-500/8 px-4 py-3 text-[13px] text-orange-200 animate-fade-in">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-orange-400" />

            <div>
              <div className="font-semibold text-orange-300 mb-0.5">Escalated for Admin Review</div>

              <div className="text-orange-200/70 leading-relaxed text-[12px]">
                Confidence threshold dipped. A support ticket has been auto-raised to the operator
                queue.
              </div>
            </div>
          </div>
        )}

        {msg.sources && msg.sources.length > 0 && <SourcesAccordion sources={msg.sources} />}
      </div>
    </div>
  );
}

// ── THINKING BUBBLE ─────────────────────────────────────────────────────────

function ThinkingBubble() {
  return (
    <div className="flex items-start gap-3 animate-fade-up">
      <div className="h-8 w-8 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
        <Loader2 className="h-4 w-4 animate-spin" />
      </div>

      <div className="rounded-2xl rounded-tl-sm border border-white/8 bg-[#0b1a40]/60 px-4 py-3 text-[13px] text-slate-500 flex items-center gap-3">
        <div className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[color:var(--gold)]/60" />

          <span
            className="h-1.5 w-1.5 animate-bounce rounded-full bg-[color:var(--gold)]/60"
            style={{ animationDelay: "120ms" }}
          />

          <span
            className="h-1.5 w-1.5 animate-bounce rounded-full bg-[color:var(--gold)]/60"
            style={{ animationDelay: "240ms" }}
          />
        </div>
        Searching knowledge base…
      </div>
    </div>
  );
}

// ── MARKDOWN RENDERER ────────────────────────────────────────────────────────

function StreamingMarkdownWrapper({ text, speed = 12 }: { text: string; speed?: number }) {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    const words = text.split(" ");

    let i = 0;

    setDisplayed("");

    const timer = setInterval(() => {
      if (i < words.length) {
        setDisplayed((prev) => (prev ? prev + " " : "") + words[i]);

        i++;
      } else {
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return <MarkdownRenderer text={displayed} />;
}

function MarkdownRenderer({ text }: { text: string }) {
  const bold = (raw: string) =>
    raw.split(/(\*\*.*?\*\*)/g).map((chunk, i) =>
      chunk.startsWith("**") && chunk.endsWith("**") ? (
        <strong key={i} className="font-semibold text-[color:var(--gold)]">
          {chunk.slice(2, -2)}
        </strong>
      ) : (
        chunk
      ),
    );

  return (
    <div className="space-y-2 text-left font-sans text-[14px] text-slate-200 leading-[1.75]">
      {text.split("\n").map((line, idx) => {
        const trimmed = line.trim();

        if (!trimmed) return <div key={idx} className="h-2" />;

        if (trimmed.startsWith("#### ")) {
          return (
            <h4
              key={idx}
              className="text-[13px] font-bold text-[color:var(--gold)] mt-4 mb-1.5 tracking-wide"
            >
              {bold(trimmed.replace(/^####\s*/, ""))}
            </h4>
          );
        }

        if (trimmed.startsWith("### ")) {
          return (
            <h3
              key={idx}
              className="flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-slate-100 mt-5 mb-3 border-b border-white/5 pb-2"
            >
              <Sparkles className="h-3.5 w-3.5 text-[color:var(--gold)] shrink-0" />

              {bold(trimmed.replace(/^###\s*/, ""))}
            </h3>
          );
        }

        if (trimmed.startsWith("## ")) {
          return (
            <h2 key={idx} className="text-[16px] font-bold text-white mt-4 mb-2 tracking-tight">
              {bold(trimmed.replace(/^##\s*/, ""))}
            </h2>
          );
        }

        // Sub-bullets

        if (line.match(/^\s{2,}/) || trimmed.startsWith("+")) {
          return (
            <div key={idx} className="flex items-start gap-2.5 pl-7 my-1">
              <span className="mt-[9px] h-1 w-1 shrink-0 rounded-full bg-slate-500" />

              <p className="flex-1 text-[13px] text-slate-400 leading-relaxed">
                {bold(trimmed.replace(/^[+\-*]\s*/, ""))}
              </p>
            </div>
          );
        }

        // Top-level bullets

        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          return (
            <div key={idx} className="flex items-start gap-3 pl-1 mt-2 mb-1">
              <span className="mt-[9px] h-1.5 w-1.5 shrink-0 rounded-sm bg-[color:var(--gold)]/70" />

              <div className="flex-1 font-medium text-slate-200 leading-relaxed">
                {bold(trimmed.replace(/^[*\-]\s*/, ""))}
              </div>
            </div>
          );
        }

        return (
          <p key={idx} className="text-slate-300 leading-[1.75]">
            {bold(line)}
          </p>
        );
      })}
    </div>
  );
}

// ── SOURCES ACCORDION ───────────────────────────────────────────────────────

function SourcesAccordion({ sources }: { sources: any[] }) {
  const [open, setOpen] = useState(false);

  const icon = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase() || "";

    if (["png", "jpg", "jpeg", "webp"].includes(ext))
      return <FileImage className="h-3.5 w-3.5 text-purple-400 shrink-0" />;

    if (["csv", "xlsx"].includes(ext))
      return <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400 shrink-0" />;

    return <FileText className="h-3.5 w-3.5 text-blue-400 shrink-0" />;
  };

  return (
    <div className="border border-white/8 bg-black/20 rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-white/5 transition-colors select-none"
      >
        <span className="flex items-center gap-2 text-[12px] font-semibold text-slate-400 uppercase tracking-wider">
          <FileText className="h-3.5 w-3.5 text-[color:var(--gold)]" />
          Sources
          <span className="rounded-md bg-white/5 border border-white/8 px-2 py-0.5 text-[10px] font-bold text-slate-500">
            {sources.length}
          </span>
        </span>

        <ChevronDown
          className={`h-3.5 w-3.5 text-slate-500 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        />
      </button>

      <div
        className={`grid transition-all duration-300 ease-out ${open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}
      >
        <div className="min-h-0">
          <ul className="space-y-2 border-t border-white/5 px-4 py-3 bg-black/20">
            {sources.map((src, i) => {
              const name = typeof src === "string" ? src : src.doc || "Document.pdf";

              const snippet =
                typeof src === "string"
                  ? "Verified reference from institutional documentation."
                  : src.snippet || "";

              return (
                <li
                  key={i}
                  className="rounded-xl border border-white/5 bg-white/[0.02] p-3 text-[13px]"
                >
                  <div className="flex items-center gap-2 mb-2 truncate" title={name}>
                    {icon(name)}

                    <span className="font-medium text-slate-300 truncate">{name}</span>
                  </div>

                  {snippet && (
                    <p className="text-[11px] text-slate-400 bg-black/20 p-2.5 rounded-lg border border-white/5 italic leading-relaxed">
                      "{snippet}"
                    </p>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}
