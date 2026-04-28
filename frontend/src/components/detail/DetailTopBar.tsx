import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

import type { BootstrapPayload } from "../../types/app";

interface DetailTopBarProps {
  pdfUrl: string;
  summaryLoading: boolean;
  summaryLabel: string;
  showSummaryAction: boolean;
  session: BootstrapPayload;
  onViewPdf: () => void;
  onGenerateSummary: () => void;
  onOpenSettings: (tab?: "settings" | "favorites") => void;
  onLogout: () => void;
}

export function DetailTopBar({
  pdfUrl,
  summaryLoading,
  summaryLabel,
  showSummaryAction,
  session,
  onViewPdf,
  onGenerateSummary,
  onOpenSettings,
  onLogout,
}: DetailTopBarProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);
  const location = useLocation();

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (event: MouseEvent) => {
      if (!menuRef.current?.contains(event.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  const initial = session.username ? session.username.slice(0, 1).toUpperCase() : "?";

  return (
    <div className="topbar">
      <div className="topbar-left">
        <a href="/" className="back-btn">
          뒤로가기
        </a>
      </div>
      <div className="topbar-center">
        <a href="/" className="topbar-logo">
          ArXplore
        </a>
      </div>
      <div className="topbar-right">
        <button type="button" className="layout-ctrl-btn" onClick={onViewPdf}>
          <svg
            className="btn-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <line x1="12" y1="3" x2="12" y2="21" />
          </svg>
          PDF 분할 보기
        </button>

        <button
          type="button"
          className="layout-ctrl-btn"
          onClick={() => window.open(pdfUrl, "_blank")}
        >
          <svg
            className="btn-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
          PDF 전체 화면
        </button>

        {showSummaryAction && (
          <button
            type="button"
            className="pdf-btn"
            onClick={onGenerateSummary}
            disabled={summaryLoading}
          >
            {summaryLoading ? "생성 중..." : summaryLabel}
          </button>
        )}

        <div className="topbar-account" ref={menuRef}>
          {!session.is_authenticated ? (
            <a className="app-header-login" href={`/login/?next=${encodeURIComponent(`${location.pathname}${location.search}`)}`}>
              로그인
            </a>
          ) : (
            <>
              <button type="button" className="account-trigger" onClick={() => setMenuOpen((v) => !v)}>
                <span className="account-trigger-badge">{initial}</span>
                <span>{session.username}</span>
              </button>
              {menuOpen ? (
                <div className="account-menu">
                  <button type="button" onClick={() => onOpenSettings("settings")}>내 설정</button>
                  <button type="button" onClick={() => onOpenSettings("favorites")}>즐겨찾기</button>
                  <button type="button" onClick={onLogout}>로그아웃</button>
                </div>
              ) : null}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
