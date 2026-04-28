export interface SummaryBlock {
  type: "heading" | "paragraph";
  text: string;
}

function normalizeSummaryHeading(line: string): string {
  return line;
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
