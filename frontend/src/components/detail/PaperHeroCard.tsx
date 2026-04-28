import type { PaperDetail } from "../../pages/detail/detail-types";

interface PaperHeroCardProps {
  paper: PaperDetail;
  isFavorited: boolean;
  canFavorite: boolean;
  onToggleFavorite: () => void;
  onRequireLogin: () => void;
}

function formatPublishedAt(raw: string): string {
  if (!raw) {
    return "-";
  }
  return raw.slice(0, 10);
}

function authorsToText(authors: PaperDetail["authors"]): string {
  if (Array.isArray(authors)) {
    return authors.join(", ");
  }
  return authors;
}

export function PaperHeroCard({ paper, isFavorited, canFavorite, onToggleFavorite, onRequireLogin }: PaperHeroCardProps) {
  return (
    <div className="card">
      <div className="paper-hero">
        <div className="paper-hero-main">
          <h1 className="paper-hero-title">{paper.title}</h1>
          <div className="paper-authors">
            <strong>저자</strong>
            <span>{authorsToText(paper.authors)}</span>
          </div>
        </div>
        <div className="paper-hero-side">
          <button
            type="button"
            className={`paper-favorite-btn ${isFavorited ? "active" : ""}`}
            onClick={canFavorite ? onToggleFavorite : onRequireLogin}
            aria-label={isFavorited ? "즐겨찾기 해제" : "즐겨찾기 추가"}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill={isFavorited ? "currentColor" : "none"}
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z" />
            </svg>
          </button>
          <div className="paper-side-item">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            <span>{formatPublishedAt(paper.published_at)}</span>
          </div>
          <div className="paper-side-item">
            <svg
              className="paper-heart-icon"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
            <span>{paper.upvotes ?? 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
