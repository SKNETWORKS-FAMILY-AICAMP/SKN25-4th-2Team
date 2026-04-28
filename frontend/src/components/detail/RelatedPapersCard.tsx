import type { RelatedPaper } from "../../pages/detail/detail-types";

interface RelatedPapersCardProps {
  papers: RelatedPaper[];
}

function truncateText(text: string | undefined | null, max: number): string {
  if (!text) {
    return "";
  }
  return text.length > max ? `${text.slice(0, max)}...` : text;
}

function authorsToText(authors: RelatedPaper["authors"]): string {
  if (Array.isArray(authors)) {
    return authors.join(", ");
  }
  return authors;
}

function buildPaperHref(paper: RelatedPaper): string {
  if (paper.source === "arxiv") {
    return `https://arxiv.org/abs/${paper.arxiv_id}`;
  }
  return `/papers/${encodeURIComponent(paper.arxiv_id)}/`;
}

export function RelatedPapersCard({ papers }: RelatedPapersCardProps) {
  if (papers.length === 0) {
    return null;
  }

  return (
    <section className="card related-papers-card">
      <div className="section-title">관련 논문</div>
      <div className="related-papers-list">
        {papers.map((paper) => (
          <a
            key={`${paper.source ?? "local"}-${paper.arxiv_id}`}
            className="related-paper-row"
            href={buildPaperHref(paper)}
            target={paper.source === "arxiv" ? "_blank" : undefined}
            rel={paper.source === "arxiv" ? "noreferrer" : undefined}
          >
            <div className="related-paper-title">{paper.title}</div>
            <div className="related-paper-meta">
              <span>{paper.published_at?.slice(0, 10) ?? "-"}</span>
              <span>{authorsToText(paper.authors)}</span>
            </div>
            {paper.abstract ? (
              <p className="related-paper-abstract">{truncateText(paper.abstract, 180)}</p>
            ) : null}
          </a>
        ))}
      </div>
    </section>
  );
}
