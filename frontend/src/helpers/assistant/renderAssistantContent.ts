function escapeHtml(value: string): string {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function normalizeArxivId(value: string): string {
  const normalized = String(value).trim().replace(/\.pdf$/i, "");
  const match = normalized.match(/^(.*)v(\d+)$/i);
  if (!match) {
    return normalized;
  }

  return match[1];
}

function toInternalPaperHref(url: string): string | null {
  const match = url.match(
    /^https?:\/\/(?:www\.)?arxiv\.org\/(?:abs|pdf)\/([^/?#]+?)(?:\.pdf)?(?:[?#].*)?$/i,
  );

  if (!match) {
    return null;
  }

  return `/papers/${normalizeArxivId(match[1])}/`;
}

function renderInlineMarkdown(text: string): string {
  let html = escapeHtml(text);
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, (_, label, url) => {
    const internalHref = toInternalPaperHref(url);
    if (internalHref) {
      return `<a href="${internalHref}">${label}</a>`;
    }

    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`;
  });
  return html;
}

export function renderAssistantContent(text: string): string {
  const lines = String(text || "").split("\n");
  const parts: string[] = [];
  let listBuffer: string[] = [];

  const flushList = () => {
    if (!listBuffer.length) {
      return;
    }
    parts.push(`<ul>${listBuffer.join("")}</ul>`);
    listBuffer = [];
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      flushList();
      continue;
    }

    if (line.startsWith("- ")) {
      listBuffer.push(`<li>${renderInlineMarkdown(line.slice(2))}</li>`);
      continue;
    }

    flushList();
    parts.push(`<p>${renderInlineMarkdown(line)}</p>`);
  }

  flushList();
  return parts.join("");
}
