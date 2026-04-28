function getCsrfTokenFromCookie(): string {
  if (typeof document === "undefined") {
    return "";
  }

  const token = document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith("csrftoken="));

  return token ? decodeURIComponent(token.split("=")[1] ?? "") : "";
}


export async function parseJsonResponse<T>(response: Response): Promise<T> {
  return (await response.json()) as T;
}


export async function fetchJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    credentials: "same-origin",
    ...init,
  });
  return parseJsonResponse<T>(response);
}


export async function fetchJsonWithBody<T>(
  input: RequestInfo | URL,
  method: "POST" | "DELETE",
  body?: unknown,
): Promise<T> {
  const csrfToken = getCsrfTokenFromCookie();
  const headers: Record<string, string> = {};
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (csrfToken) {
    headers["X-CSRFToken"] = csrfToken;
  }

  return fetchJson<T>(input, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}


export { getCsrfTokenFromCookie };
