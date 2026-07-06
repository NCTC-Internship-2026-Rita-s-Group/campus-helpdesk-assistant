import { auth } from "./firebase"; // 🚀 Imported to intercept active sessions dynamically

// ==============================================================================

// 📊 TYPE-SAFE ENTERPRISE CONTRACT INTERFACES

// ==============================================================================

export interface Notice {
  id: number; // Synchronized with your database auto-incrementing integer key

  title: string;

  category: string;

  excerpt?: string;

  content: string;
}

export interface TicketTimeline {
  date: string;

  message: string;
}

export interface Ticket {
  id: string; // e.g., "TK-2026-1234" string formats

  subject: string;

  category: string;

  created_date: string; // Synchronized with backend snake_case database schema row

  status: string;

  priority: string;

  description: string;

  timeline: TicketTimeline[];
}

export interface KBDocument {
  id: string;

  filename: string;

  fileSize: string;

  format: string;

  uploadedAt: string;

  status: "Processing" | "Indexed" | "Failed";
}

export interface LiveChatMessage {
  id: string;

  role: "user" | "assistant";

  createdAt: number;

  content: string;

  context_verified?: boolean; // Real-time feedback if text was verified by official circulars

  sources?: string[]; // Simple array of active source document string citations
}

// 🔐 DUAL-FACETED AUTHENTICATION PAYLOAD SCHEMAS

export interface UserIdentitySyncResponse {
  uid: string;

  email: string;

  name: string;

  role: string;

  redirect_target: string;

  is_active: bool;
}

export interface AdminLoginResponse {
  uid: string;

  email: string;

  name: string;

  role: string;

  custom_token: string; // Firebase custom token returned by backend for client mirroring

  redirect_target: string;
}

// Fixed base route mapping our corporate API version boundaries cleanly

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

/**

 * 🔒 Enterprise Token Extraction Helper

 * Fetches the live, short-lived JSON Web Token (JWT) directly from the Firebase context

 * and appends it as a Bearer token to the request headers.

 */

async function getAuthHeaders(customHeaders: Record<string, string> = {}): Promise<HeadersInit> {
  const firebaseUser = auth.currentUser;

  const headers: Record<string, string> = { ...customHeaders };

  if (firebaseUser) {
    const token = await firebaseUser.getIdToken();

    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

// ==============================================================================

// 🚀 CENTRALIZED ASYNCHRONOUS API NETWORK CONDUIT CLIENT

// ==============================================================================

export const apiClient = {
  /**

   * 🎓 Student: Synchronize active Firebase session and discover authorization role

   */

  async syncUserSession(idToken: string): Promise<UserIdentitySyncResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/sync`, {
      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ id_token: idToken }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "Sync failed" }));

      throw new Error(errorData.detail || "Identity platform synchronization deadlock.");
    }

    return (await response.json()) as UserIdentitySyncResponse;
  },

  /**

   * 👑 Admin: Authenticate using private credentials via username exchange

   */

  async adminLogin(username: string, password: string): Promise<AdminLoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/admin-login`, {
      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "Login failed" }));

      throw new Error(errorData.detail || "Administrative credential verification rejected.");
    }

    return (await response.json()) as AdminLoginResponse;
  },

  /**

   * 👑 Admin Dashboard: Programmatically provision a new administrative operator account

   */

  async createAdmin(
    fullName: string,

    email: string,

    username: string,

    password: string,
  ): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/create-admin`, {
      method: "POST",

      headers: await getAuthHeaders({ "Content-Type": "application/json" }),

      body: JSON.stringify({ full_name: fullName, email, username, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "Provisioning failed" }));

      throw new Error(errorData.detail || "Failed to execute administrative account allocation.");
    }

    return await response.json();
  },

  /**

   * 📋 Fetch Live Notices & Announcements

   */

  async getNotices(): Promise<Notice[]> {
    const response = await fetch(`${API_BASE_URL}/notices`, {
      headers: await getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to load notices ledger: ${response.statusText}`);
    }

    return (await response.json()) as Notice[];
  },

  /**

   * 🎫 Fetch Live Grievance Tickets

   */

  async getTickets(): Promise<Ticket[]> {
    const response = await fetch(`${API_BASE_URL}/tickets`, {
      headers: await getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to pull institutional ticket indexes: ${response.statusText}`);
    }

    return (await response.json()) as Ticket[];
  },

  /**

   * 🛠️ Admin: Update an existing ticket's operational status

   */

  async updateTicketStatus(id: string, status: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}/status`, {
      method: "PATCH",

      headers: await getAuthHeaders({ "Content-Type": "application/json" }),

      body: JSON.stringify({ status }),
    });

    if (!response.ok) {
      throw new Error(`Failed to patch operational lifecycle status for ticket entry: ${id}`);
    }

    return response.ok;
  },

  /**

   * 📢 Admin: Broadcast a brand new official announcement circular

   */

  async createNotice(title: string, category: string, content: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}/notices`, {
      method: "POST",

      headers: await getAuthHeaders({ "Content-Type": "application/json" }),

      body: JSON.stringify({ title, category, content }),
    });

    if (!response.ok) {
      throw new Error(
        `Failed to execute backend system bulletin broadcast: ${response.statusText}`,
      );
    }

    return response.ok;
  },

  /**

   * 📤 Admin RAG: Stream document binary straight to your background worker pipeline

   */

  async uploadKBDocument(file: File): Promise<boolean> {
    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",

      headers: await getAuthHeaders(),

      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Document ingestion gateway processing failure: ${response.statusText}`);
    }

    return response.ok;
  },

  /**

   * 🧠 Admin RAG: Fetch all registered knowledge base indexed documents

   */

  async getKBDocuments(): Promise<KBDocument[]> {
    const response = await fetch(`${API_BASE_URL}/documents`, {
      headers: await getAuthHeaders(),
    });

    if (!response.ok) {
      return [];
    }

    return (await response.json()) as KBDocument[];
  },

  /**

   * 🎫 Student: Initialize and submit a brand new formal campus grievance ticket

   */

  async createTicket(
    subject: string,

    category: string,

    priority: string,

    description: string,
  ): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}/tickets`, {
      method: "POST",

      headers: await getAuthHeaders({ "Content-Type": "application/json" }),

      body: JSON.stringify({ subject, category, priority, description }),
    });

    if (!response.ok) {
      throw new Error(
        `Failed to commit grievance ticket registry sequence: ${response.statusText}`,
      );
    }

    return response.ok;
  },

  /**

   * 💬 Student AI: Send query loops straight into your local LLaMA 3.3 RAG Orchestrator

   */

  async sendChatMessage(
    prompt: string,

    history: { role: "user" | "assistant"; content: string }[],

    conversationId?: string,
  ): Promise<
    LiveChatMessage & {
      answer: string;

      generated_title?: string;

      supplemental_data: string;

      error: string;
    }
  > {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",

      headers: await getAuthHeaders({ "Content-Type": "application/json" }),

      body: JSON.stringify({
        question: prompt,

        history: history,

        conversation_id: conversationId || null,
      }),
    });

    if (!response.ok) {
      throw new Error(`Inference engine connection deadlock: ${response.statusText}`);
    }

    const data = (await response.json()) as {
      answer: string;

      sources: string[];

      context_verified: boolean;

      generated_title?: string;

      supplemental_data?: string;

      error?: string;
    };

    return {
      id: `reply-${Date.now()}`,

      role: "assistant",

      createdAt: Date.now(),

      content: data.answer || "",

      answer: data.answer || "",

      context_verified: data.context_verified ?? false,

      sources: data.sources || [],

      generated_title: data.generated_title || undefined,

      supplemental_data: data.supplemental_data || "",

      error: data.error || "",
    };
  },
};
