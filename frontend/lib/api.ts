const DEFAULT_API_PORT = "8000";

/** Resolve local API requests against the same hostname used by the browser.
 * This keeps localhost and 127.0.0.1 session cookies from becoming cross-site.
 */
export function getApiBase(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (typeof window === "undefined") {
    return configured || `http://localhost:${DEFAULT_API_PORT}`;
  }

  const browserHost = window.location.hostname;
  const base = new URL(configured || `${window.location.protocol}//${browserHost}:${DEFAULT_API_PORT}`);
  if ((base.hostname === "localhost" || base.hostname === "127.0.0.1") && (browserHost === "localhost" || browserHost === "127.0.0.1")) {
    base.hostname = browserHost;
  }
  return base.origin;
}
