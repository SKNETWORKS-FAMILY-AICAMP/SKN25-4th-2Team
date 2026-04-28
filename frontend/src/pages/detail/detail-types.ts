export type ChatRole = "assistant" | "user";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface PaperDetail {
  arxiv_id: string;
  title: string;
  authors: string[] | string;
  abstract: string;
  published_at: string;
  upvotes?: number | null;
  pdf_url: string;
  is_favorited?: boolean;
}

export interface DetailResponse {
  paper?: PaperDetail;
  error?: string;
}

export interface AnalysisResponse {
  overview?: string;
  key_findings?: string[];
  cached?: boolean;
  error?: string;
}

export interface SummaryResponse {
  summary?: string;
  cached?: boolean;
  model?: string;
  error?: string;
}

export interface ChatResponse {
  answer?: string;
  error?: string;
}
