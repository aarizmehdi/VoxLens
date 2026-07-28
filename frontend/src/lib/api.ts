/**
 * VoxLens — API Client
 *
 * Typed fetch wrapper for all backend API calls.
 */

const API_BASE = "/api";

// ============================================================
// Types
// ============================================================

export interface Meeting {
  id: string;
  title: string | null;
  source_type: string;
  source_url: string | null;
  file_name: string | null;
  language: string;
  status: string;
  error_message: string | null;
  progress: number;
  duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface MeetingListResponse {
  meetings: Meeting[];
  total: number;
}

export interface TranscriptChunk {
  id: string;
  chunk_index: number;
  start_time: number;
  end_time: number;
  text: string;
}

export interface TranscriptResponse {
  meeting_id: string;
  chunks: TranscriptChunk[];
  full_text: string;
}

export interface ActionItem {
  task: string;
  owner: string;
  deadline: string;
}

export interface SummaryReport {
  meeting_id: string;
  summary: string | null;
  bullet_points: string[] | null;
  key_takeaways: string[] | null;
  action_items: ActionItem[] | null;
  decisions: string[] | null;
  open_questions: string[] | null;
  created_at: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: ChatSource[] | null;
  created_at: string;
}

export interface ChatSource {
  chunk_index: number;
  text: string;
  relevance: number;
}

export interface ChatResponse {
  message: ChatMessage;
  sources: ChatSource[] | null;
}

export interface JobStatus {
  meeting_id: string;
  status: string;
  progress: number;
  error_message: string | null;
}

export interface ExportResponse {
  meeting_id: string;
  markdown: string;
  filename: string;
}

// ============================================================
// Fetch Helpers
// ============================================================

class ApiError extends Error {
  status: number;
  
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || "Request failed");
  }

  return res.json();
}

// ============================================================
// API Functions
// ============================================================

// --- Processing ---

export async function processUrl(
  url: string,
  language: string = "auto",
): Promise<Meeting> {
  return request<Meeting>("/process/url", {
    method: "POST",
    body: JSON.stringify({ url, language }),
  });
}

export async function processUpload(
  file: File,
  language: string = "auto",
): Promise<Meeting> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", language);

  const url = `${API_BASE}/process/upload`;
  const res = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || "Upload failed");
  }

  return res.json();
}

// --- Jobs ---

export async function getJobStatus(meetingId: string): Promise<JobStatus> {
  return request<JobStatus>(`/jobs/${meetingId}`);
}

// --- Meetings ---

export async function getMeetings(
  skip: number = 0,
  limit: number = 20,
): Promise<MeetingListResponse> {
  return request<MeetingListResponse>(
    `/meetings?skip=${skip}&limit=${limit}`,
  );
}

export async function getMeeting(meetingId: string): Promise<Meeting> {
  return request<Meeting>(`/meetings/${meetingId}`);
}

export async function deleteMeeting(meetingId: string): Promise<void> {
  await request(`/meetings/${meetingId}`, { method: "DELETE" });
}

// --- Transcripts ---

export async function getTranscript(
  meetingId: string,
): Promise<TranscriptResponse> {
  return request<TranscriptResponse>(`/transcripts/${meetingId}`);
}

// --- Reports ---

export async function getReport(meetingId: string): Promise<SummaryReport> {
  return request<SummaryReport>(`/report/${meetingId}`);
}

// --- Chat ---

export async function sendChatMessage(
  meetingId: string,
  message: string,
): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ meeting_id: meetingId, message }),
  });
}

export async function getChatHistory(
  meetingId: string,
): Promise<ChatMessage[]> {
  return request<ChatMessage[]>(`/chat/${meetingId}/history`);
}

// --- Export ---

export async function exportMeeting(
  meetingId: string,
): Promise<ExportResponse> {
  return request<ExportResponse>(`/export/${meetingId}`);
}
