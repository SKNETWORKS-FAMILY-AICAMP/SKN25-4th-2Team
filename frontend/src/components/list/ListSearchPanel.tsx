import type { FormEvent } from "react";
import type { SearchMode } from "../../pages/list/listTypes";

const SEARCH_MODE_CONFIG: Record<
  SearchMode,
  { helper: string; placeholder: string }
> = {
  search: {
    helper: "Search papers by title or abstract.",
    placeholder: "Search papers by title or abstract",
  },
  ai: {
    helper: "Search any papers with AI.",
    placeholder: "Search any papers with AI",
  },
};

interface ListSearchPanelProps {
  mode: SearchMode;
  queryInput: string;
  onModeChange: (mode: SearchMode) => void;
  onQueryInputChange: (value: string) => void;
  onSubmit: () => void;
  busy: boolean;
}

export function ListSearchPanel({
  mode,
  queryInput,
  onModeChange,
  onQueryInputChange,
  onSubmit,
  busy,
}: ListSearchPanelProps) {
  const config = SEARCH_MODE_CONFIG[mode];

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <div className="smart-search-container">
      <div className="search-shell">
        <div className="search-mode-row">
          <div className="search-mode-segment" role="tablist" aria-label="검색 모드 선택">
            <button
              type="button"
              className={`mode-chip${mode === "search" ? " active" : ""}`}
              data-mode="search"
              onClick={() => onModeChange("search")}
            >
              키워드 검색
            </button>
            <button
              type="button"
              className={`mode-chip${mode === "ai" ? " active" : ""}`}
              data-mode="ai"
              onClick={() => onModeChange("ai")}
            >
              AI 어시스턴트
            </button>
          </div>
          <div className="search-mode-helper">{config.helper}</div>
        </div>

        <form className="pill-search-bar" onSubmit={handleSubmit}>
          <input
            type="text"
            name="q"
            value={queryInput}
            placeholder={config.placeholder}
            autoComplete="off"
            onChange={(event) => onQueryInputChange(event.target.value)}
          />
          <div className="search-actions-right">
            <button type="submit" className="submit-btn-premium" disabled={busy}>
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              Search
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
