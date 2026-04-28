export interface SummaryBlock {
  type: "heading" | "paragraph";
  text: string;
}

const SUMMARY_HEADER_MAP: Record<string, string> = {
  "문제 정의": "Problem Definition",
  "접근 방법": "Methodology",
  "실험 및 결과": "Experiments & Results",
  "한계": "Limitations",
  "핵심 가치": "Core Values",
  "읽는 포인트": "Key Highlights",
};

function normalizeSummaryHeading(line: string): string {
  let normalizedLine = line;

  for (const [korean, english] of Object.entries(SUMMARY_HEADER_MAP)) {
    if (normalizedLine.startsWith(`## ${korean}`)) {
      normalizedLine = normalizedLine.replace(`## ${korean}`, `## ${english}`);
    }
  }

  return normalizedLine;
}

export function formatSummaryBlocks(text: string): SummaryBlock[] {
  if (!text) {
    return [];
  }

  return text
    .split("\n")
    .map((line) => normalizeSummaryHeading(line))
    .filter((line) => line.trim().length > 0)
    .map((line) => {
      if (line.startsWith("## ")) {
        return { type: "heading", text: line.replace("## ", "").trim() };
      }
      return { type: "paragraph", text: line };
    });
}
