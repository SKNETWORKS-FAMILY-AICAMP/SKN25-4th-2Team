import type { PaperListResponse, SearchMode, SortOption } from "./listTypes";

interface ListQuery {
  q: string;
  sort: SortOption;
  mode: SearchMode;
  page: number;
}

interface ErrorPayload {
  error?: string;
}

function extractError(payload: unknown, fallback: string): string {
  if (
    payload &&
    typeof payload === "object" &&
    "error" in payload &&
    typeof (payload as ErrorPayload).error === "string"
  ) {
    return (payload as ErrorPayload).error as string;
  }
  return fallback;
}

export async function fetchPaperList(
  query: ListQuery,
  signal?: AbortSignal,
): Promise<PaperListResponse> {
  const params = new URLSearchParams();
  if (query.q) {
    params.set("q", query.q);
  }
  params.set("sort", query.sort);
  params.set("mode", query.mode);
  params.set("page", String(query.page));

  const response = await fetch(`/papers/list.json?${params.toString()}`, {
    method: "GET",
    credentials: "same-origin",
    signal,
  });

  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new Error(extractError(payload, "목록을 불러오지 못했습니다."));
  }

  return payload as PaperListResponse;
}
