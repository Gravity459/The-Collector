import axios from "axios";

/**
 * Client-side axios instance. Talks to same-origin Next route handlers under
 * `/api/*`, which proxy to the backend and attach the httpOnly JWT cookie.
 */
export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});
