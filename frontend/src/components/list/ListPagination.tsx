interface ListPaginationProps {
  page: number;
  totalPages: number;
  query: string;
  sort: string;
  mode: string;
  onPageChange: (page: number) => void;
}

function clampPage(page: number, totalPages: number): number {
  if (page < 1) {
    return 1;
  }
  if (page > totalPages) {
    return totalPages;
  }
  return page;
}

export function ListPagination({
  page,
  totalPages,
  query,
  sort,
  mode,
  onPageChange,
}: ListPaginationProps) {
  const prevPage = clampPage(page - 1, totalPages);
  const nextPage = clampPage(page + 1, totalPages);
  const jumpPrev10 = clampPage(page - 10, totalPages);
  const jumpNext10 = clampPage(page + 10, totalPages);

  const buildHref = (targetPage: number): string => {
    const params = new URLSearchParams();
    if (query) {
      params.set("q", query);
    }
    params.set("sort", sort);
    params.set("mode", mode);
    params.set("page", String(targetPage));
    return `/?${params.toString()}`;
  };

  const canGoPrev = page > 1;
  const canGoNext = page < totalPages;

  return (
    <nav className="pagination" aria-label="pagination">
      {canGoPrev ? (
        <>
          <a
            className="arrow"
            href={buildHref(jumpPrev10)}
            onClick={(event) => {
              event.preventDefault();
              onPageChange(jumpPrev10);
            }}
          >
            &laquo;
          </a>
          <a
            className="arrow"
            href={buildHref(prevPage)}
            onClick={(event) => {
              event.preventDefault();
              onPageChange(prevPage);
            }}
          >
            &lsaquo;
          </a>
        </>
      ) : (
        <>
          <span className="arrow disabled">&laquo;</span>
          <span className="arrow disabled">&lsaquo;</span>
        </>
      )}

      <span className="page-info">
        {page} / {totalPages}
      </span>

      {canGoNext ? (
        <>
          <a
            className="arrow"
            href={buildHref(nextPage)}
            onClick={(event) => {
              event.preventDefault();
              onPageChange(nextPage);
            }}
          >
            &rsaquo;
          </a>
          <a
            className="arrow"
            href={buildHref(jumpNext10)}
            onClick={(event) => {
              event.preventDefault();
              onPageChange(jumpNext10);
            }}
          >
            &raquo;
          </a>
        </>
      ) : (
        <>
          <span className="arrow disabled">&rsaquo;</span>
          <span className="arrow disabled">&raquo;</span>
        </>
      )}
    </nav>
  );
}
