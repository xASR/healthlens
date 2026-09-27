// Render's free tier sleeps the backend after inactivity; the first request
// afterwards can take 50+ seconds. Pinging /health as soon as the SPA loads
// starts that boot while the user is still on the landing or login page.
//
// /health is mounted at the app root, outside the /api/v1 prefix, so it is
// derived from VITE_API_BASE_URL rather than called through apiClient.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
const HEALTH_URL = `${API_BASE.replace(/\/api\/v1\/?$/, "")}/health`;

let started = false;

export function warmUpServer() {
  // Relative bases (Vite dev proxy) only proxy /api, so skip those.
  if (started || !/^https?:\/\//.test(API_BASE)) return;
  started = true;
  // no-cors: the response is never read, and this avoids any CORS dependency.
  fetch(HEALTH_URL, { mode: "no-cors", cache: "no-store" }).catch(() => {});
}
