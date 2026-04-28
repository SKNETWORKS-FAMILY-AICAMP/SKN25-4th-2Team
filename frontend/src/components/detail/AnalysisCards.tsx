import type { SummaryBlock } from "../../pages/detail/detail-summary";

interface AbstractCardProps {
  abstractText: string;
  noticeText?: string;
}

export function AbstractCard({ abstractText, noticeText }: AbstractCardProps) {
  return (
    <>
      {noticeText ? <div className="info-box">{noticeText}</div> : null}
      <div className="card">
        <div className="section-title">초록</div>
        <div className="overview-text">{abstractText}</div>
      </div>
    </>
  );
}

interface OverviewCardProps {
  loading: boolean;
  overviewText: string;
  errorText: string;
}

function splitParagraphs(text: string): string[] {
  return text
    .replace(/\r\n/g, "\n")
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
}

export function OverviewCard({
  loading,
  overviewText,
  errorText,
}: OverviewCardProps) {
  const paragraphs = overviewText ? splitParagraphs(overviewText) : [];

  return (
    <div className="card" id="overview-card">
      <div className="section-title section-title-between">
        <span className="section-title-inline">
          개요
          {loading && (
            <span id="overview-loading" className="loading-inline">
              <span className="spinner" />
              <span className="loading-text">분석 중...</span>
            </span>
          )}
        </span>
      </div>
      {paragraphs.length > 0 && (
        <div id="overview-content" className="overview-text">
          {paragraphs.map((text, idx) => (
            <p key={`p-${idx}`}>{text}</p>
          ))}
        </div>
      )}
      {errorText && (
        <div id="overview-error" className="error-box">
          {errorText}
        </div>
      )}
    </div>
  );
}

interface FindingsCardProps {
  findings: string[];
}

export function FindingsCard({ findings }: FindingsCardProps) {
  if (!findings.length) {
    return null;
  }

  return (
    <div className="card" id="findings-card">
      <div className="section-title">핵심 포인트</div>
      <ul className="key-findings" id="findings-list">
        {findings.map((finding, idx) => (
          <li key={`${idx}-${finding.slice(0, 24)}`}>{finding}</li>
        ))}
      </ul>
    </div>
  );
}

interface SummaryCardProps {
  blocks: SummaryBlock[];
  errorText: string;
}

export function SummaryCard({ blocks, errorText }: SummaryCardProps) {
  if (!blocks.length && !errorText) {
    return null;
  }

  return (
    <div id="summary-card" className="card">
      <div id="summary-content" className="summary-text">
        {blocks.map((block, idx) =>
          block.type === "heading" ? (
            <h2 key={`${idx}-${block.text}`}>{block.text}</h2>
          ) : (
            <p key={`${idx}-${block.text}`}>{block.text}</p>
          ),
        )}
      </div>
      {errorText && (
        <div id="summary-error" className="error-box summary-error">
          {errorText}
        </div>
      )}
    </div>
  );
}
