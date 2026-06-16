// ============================================================
// api.js — all backend calls in one place
// Change this URL after you deploy to Render
// ============================================================
// Detect if running locally or in production
const API_BASE = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://127.0.0.1:8000"
  : "https://jobportal-production.up.railway.app"; // Update this with your actual Railway URL if it differs


// ── token helpers ────────────────────────────────────────────
function saveAuth(data) {
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("role", data.role);
  localStorage.setItem("full_name", data.full_name);
  localStorage.setItem("user_id", data.user_id);
}

function getToken() { return localStorage.getItem("token"); }
function getRole()  { return localStorage.getItem("role"); }
function getName()  { return localStorage.getItem("full_name"); }
function logout()   { localStorage.clear(); window.location.href = "login.html"; }
function isLoggedIn() { return !!getToken(); }

function authHeaders() {
  return { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}` };
}

// ── generic request ──────────────────────────────────────────
async function request(method, path, body = null, auth = false) {
  const options = { method, headers: auth ? authHeaders() : { "Content-Type": "application/json" } };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(API_BASE + path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Something went wrong");
  return data;
}

// ── auth ─────────────────────────────────────────────────────
const Auth = {
  register: (payload) => request("POST", "/auth/register", payload),
  login:    (payload) => request("POST", "/auth/login", payload),
};

// ── user ─────────────────────────────────────────────────────
const User = {
  me:     ()       => request("GET",  "/users/me", null, true),
  update: (payload) => request("PUT",  "/users/me", payload, true),
};

// ── jobs ─────────────────────────────────────────────────────
const Jobs = {
  getAll:  (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    return request("GET", `/jobs/${params ? "?" + params : ""}`);
  },
  search:  (keyword) => request("GET", `/jobs/search?keyword=${encodeURIComponent(keyword)}`),
  getOne:  (id)      => request("GET", `/jobs/${id}`),
  create:  (payload) => request("POST", "/jobs/", payload, true),
  update:  (id, payload) => request("PUT", `/jobs/${id}`, payload, true),
  delete:  (id)      => request("DELETE", `/jobs/${id}`, null, true),
};

// ── applications ─────────────────────────────────────────────
const Applications = {
  apply:        (payload) => request("POST", "/applications/", payload, true),
  mine:         ()        => request("GET",  "/applications/my", null, true),
  forJob:       (job_id)  => request("GET",  `/applications/job/${job_id}`, null, true),
  updateStatus: (app_id, status) => request("PUT", `/applications/${app_id}/status`, { status }, true),
};

// ── bookmarks ────────────────────────────────────────────────
const Bookmarks = {
  save: (job_id) => request("POST", "/bookmarks/", { job_id }, true),
  mine: ()       => request("GET",  "/bookmarks/my", null, true),
};

// ── dashboard ────────────────────────────────────────────────
const Dashboard = {
  stats: () => request("GET", "/dashboard/stats"),
};
