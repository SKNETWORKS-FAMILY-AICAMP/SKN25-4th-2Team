function readCookieValue(cookieName: string): string {
  if (typeof document === "undefined") {
    return "";
  }

  const cookies = document.cookie ? document.cookie.split(";") : [];
  for (const rawCookie of cookies) {
    const cookie = rawCookie.trim();
    if (!cookie.startsWith(`${cookieName}=`)) {
      continue;
    }
    return decodeURIComponent(cookie.slice(cookieName.length + 1));
  }

  return "";
}

export function getCsrfTokenFromCookie(): string {
  return readCookieValue("csrftoken");
}
