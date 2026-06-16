# Job Portal System

A full-stack web application connecting job seekers with employers.

**Built with:** FastAPI · PostgreSQL (Supabase) · HTML/CSS · JWT Auth  
**Deployed on:** Railway (backend) · Netlify (frontend)

---

## Live Links

| | Link |
|---|---|
| Frontend | [f2024408250-jobportal.netlify.app](https://f2024408250-jobportal.netlify.app) |
| Backend API | [jobportal-production.up.railway.app](https://jobportal-production.up.railway.app) |
| API Docs | [jobportal-production.up.railway.app/docs](https://jobportal-production.up.railway.app/docs) |
| GitHub | [github.com/f2024408250-bot/JobPortal](https://github.com/f2024408250-bot/JobPortal) |

---

## Project Structure

```
JobPortal/
├── backend/
│   ├── main.py          # All 17 API endpoints
│   ├── models.py        # SQLAlchemy table models
│   ├── schemas.py       # Pydantic request/response models
│   ├── database.py      # Supabase connection
│   ├── auth.py          # JWT authentication
│   ├── requirements.txt
│   └── .env             # Your credentials (never push this)
├── frontend/
│   ├── index.html           # Home page
│   ├── login.html           # Login / Register
│   ├── jobs.html            # Browse & filter jobs
│   ├── job-detail.html      # Single job + Apply
│   ├── seeker-dashboard.html
│   ├── employer-dashboard.html
│   ├── about.html
│   ├── css/style.css        # Shared stylesheet
│   └── js/api.js            # All fetch calls to backend
├── supabase_tables.sql  # Run this in Supabase SQL Editor
└── README.md
```

---

## Setup Instructions

### Step 1 — Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a free project
2. Open **SQL Editor** from the left sidebar
3. Paste the contents of `supabase_tables.sql` and click **Run**
4. Go to **Project Settings → Database → Connection String → URI**
5. Copy the connection string

### Step 2 — Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Open `.env` and fill in your values:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
SECRET_KEY=any_long_random_string_here
```

Run the backend:
```bash
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test all APIs.

### Step 3 — Frontend Setup

No installation needed. Just open `frontend/index.html` in your browser.

Make sure the backend is running first. The `api.js` file points to `http://127.0.0.1:8000` by default.

### Step 4 — Deployment

**Backend (Railway):**
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Choose the `JobPortal` repository
4. Add environment variables: `DATABASE_URL` and `SECRET_KEY`
5. Railway will automatically build and deploy using the root `railway.json` file.

**Frontend (Netlify):**
1. Open `frontend/js/api.js`
2. Change `API_BASE` from `http://127.0.0.1:8000` to your Render URL
3. Go to [netlify.com](https://netlify.com) → Drag and drop your `frontend` folder

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login and get JWT token |
| GET | /users/me | Get my profile |
| PUT | /users/me | Update my profile |
| POST | /jobs/ | Post a new job |
| GET | /jobs/ | Get all jobs (with filters) |
| GET | /jobs/search | Search jobs by keyword |
| GET | /jobs/{id} | Get single job |
| PUT | /jobs/{id} | Update job |
| DELETE | /jobs/{id} | Delete job |
| POST | /applications/ | Apply to a job |
| GET | /applications/my | My applications |
| GET | /applications/job/{id} | Applications for a job |
| PUT | /applications/{id}/status | Update application status |
| POST | /bookmarks/ | Bookmark a job |
| GET | /bookmarks/my | My bookmarks |
| GET | /dashboard/stats | System statistics |

---

## Database Tables

- **users** — Job seekers and employers
- **jobs** — Job listings posted by employers
- **applications** — Applications submitted by job seekers
- **bookmarks** — Saved jobs by job seekers

---

*Hamza Hassan · F2024408250 · UMT OSSD Y9 · 2026*
