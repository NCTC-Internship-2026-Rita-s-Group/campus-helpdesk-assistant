export type Citation = {
  doc: string;
  page: number;
  snippet: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Citation[];
  escalated?: boolean;
  confidence?: number;
  ticketId?: string;
  createdAt: number;
};

export type ChatSession = {
  id: string;
  title: string;
  updatedAt: number;
  messages: ChatMessage[];
};

const SAMPLE_REPLIES: Array<{
  match: RegExp;
  reply: Omit<ChatMessage, "id" | "role" | "createdAt">;
}> = [
  {
    match: /hostel|accommodation|room/i,
    reply: {
      content:
        "Hostel allotment for the 2025-26 session is finalised by the Hostel Office within ten working days of admission confirmation. Single-occupancy is prioritised for final-year and PhD scholars; double-occupancy is the default for incoming cohorts. Mess fees are billed quarterly along with the hostel fee.",
      confidence: 0.91,
      sources: [
        {
          doc: "hostel_policy_2025.pdf",
          page: 4,
          snippet:
            "Allotment of hostel rooms shall be completed within 10 working days from the date of admission confirmation, subject to availability.",
        },
        {
          doc: "hostel_policy_2025.pdf",
          page: 7,
          snippet:
            "Single-occupancy rooms are reserved for final-year undergraduate and doctoral scholars on a first-come basis.",
        },
      ],
    },
  },
  {
    match: /exam|result|semester|grade/i,
    reply: {
      content:
        "End-semester examinations begin in the third week of May. Hall tickets are released on the student portal seven days prior. Re-evaluation requests must be submitted within fifteen days of result publication through the Examination Cell portal.",
      confidence: 0.87,
      sources: [
        {
          doc: "examination_handbook.pdf",
          page: 12,
          snippet:
            "Hall tickets shall be made available on the student portal not later than 7 days before the commencement of end-semester examinations.",
        },
      ],
    },
  },
  {
    match: /placement|internship|career/i,
    reply: {
      content:
        "Placement registration for the 2026 batch is currently open on the CRC portal. Pre-placement talks begin the first week of August. Eligibility requires a minimum CGPA of 6.5 with no active backlogs.",
      confidence: 0.82,
      sources: [
        {
          doc: "placement_policy.pdf",
          page: 3,
          snippet:
            "Students with a CGPA of 6.5 or above and no active backlogs at the time of registration are eligible to participate in campus recruitment.",
        },
      ],
    },
  },
  {
    match: /scholarship|fee waiver|financial aid/i,
    reply: {
      content:
        "I could not find a verified, up-to-date answer in the current knowledge base. A support ticket has been raised so the Student Affairs office can respond directly.",
      confidence: 0.42,
    },
  },
];

const FALLBACK: Omit<ChatMessage, "id" | "role" | "createdAt"> = {
  content:
    "I want to make sure the answer is accurate, but the current knowledge base does not have a confident match for your question. I have flagged this for an administrator who will follow up shortly.",
  confidence: 0.51,
};

const newId = () =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

export function getMockReply(prompt: string): ChatMessage {
  const found = SAMPLE_REPLIES.find((r) => r.match.test(prompt));
  const base = found?.reply ?? FALLBACK;
  const escalated = (base.confidence ?? 1) < 0.6;
  return {
    id: newId(),
    role: "assistant",
    createdAt: Date.now(),
    ...base,
    escalated,
    ticketId: escalated ? "TKT-" + Math.floor(1000 + Math.random() * 9000) : undefined,
  };
}

export function createSession(title = "New conversation"): ChatSession {
  return { id: newId(), title, updatedAt: Date.now(), messages: [] };
}

export function makeUserMessage(content: string): ChatMessage {
  return { id: newId(), role: "user", content, createdAt: Date.now() };
}