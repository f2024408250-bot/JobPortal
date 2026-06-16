from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
import models, schemas
from auth import hash_password, verify_password, create_access_token, get_current_user

import os

app = FastAPI(title="Job Portal System", version="1.0.0")

frontend_dir = "../frontend"
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 1. REGISTER ───────────────────────────────────────────────────────────────
@app.post("/auth/register", response_model=schemas.TokenResponse, status_code=201)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if data.role not in ["jobseeker", "employer"]:
        raise HTTPException(status_code=400, detail="Role must be jobseeker or employer")

    user = models.User(
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        company_name=data.company_name if data.role == "employer" else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "full_name": user.full_name, "user_id": user.id}


# ── 2. LOGIN ──────────────────────────────────────────────────────────────────
@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "full_name": user.full_name, "user_id": user.id}


# ── 3. GET MY PROFILE ─────────────────────────────────────────────────────────
@app.get("/users/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


# ── 4. UPDATE MY PROFILE ──────────────────────────────────────────────────────
@app.put("/users/me", response_model=schemas.UserResponse)
def update_my_profile(data: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if data.full_name:
        current_user.full_name = data.full_name
    if data.bio is not None:
        current_user.bio = data.bio
    if data.skills is not None:
        current_user.skills = data.skills
    if data.company_name is not None:
        current_user.company_name = data.company_name
    db.commit()
    db.refresh(current_user)
    return current_user


# ── 5. POST A JOB ─────────────────────────────────────────────────────────────
@app.post("/jobs/", response_model=schemas.JobResponse, status_code=201)
def post_job(data: schemas.JobCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Only employers can post jobs")

    job = models.Job(employer_id=current_user.id, **data.dict())
    db.add(job)
    db.commit()
    db.refresh(job)

    response = schemas.JobResponse.from_orm(job)
    response.employer_name = current_user.full_name
    response.company_name = current_user.company_name
    return response


# ── 6. GET ALL JOBS ───────────────────────────────────────────────────────────
@app.get("/jobs/", response_model=List[schemas.JobResponse])
def get_all_jobs(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None)
):
    query = db.query(models.Job).filter(models.Job.is_active == True)
    if category:
        query = query.filter(models.Job.category.ilike(f"%{category}%"))
    if location:
        query = query.filter(models.Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(models.Job.job_type == job_type)

    jobs = query.order_by(models.Job.created_at.desc()).all()
    result = []
    for job in jobs:
        r = schemas.JobResponse.from_orm(job)
        r.employer_name = job.employer.full_name
        r.company_name = job.employer.company_name
        result.append(r)
    return result


# ── 7. SEARCH JOBS ────────────────────────────────────────────────────────────
@app.get("/jobs/search", response_model=List[schemas.JobResponse])
def search_jobs(keyword: str = Query(...), db: Session = Depends(get_db)):
    jobs = db.query(models.Job).filter(
        models.Job.is_active == True,
        (models.Job.title.ilike(f"%{keyword}%")) |
        (models.Job.description.ilike(f"%{keyword}%")) |
        (models.Job.category.ilike(f"%{keyword}%"))
    ).order_by(models.Job.created_at.desc()).all()

    result = []
    for job in jobs:
        r = schemas.JobResponse.from_orm(job)
        r.employer_name = job.employer.full_name
        r.company_name = job.employer.company_name
        result.append(r)
    return result


# ── 8. GET SINGLE JOB ─────────────────────────────────────────────────────────
@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    r = schemas.JobResponse.from_orm(job)
    r.employer_name = job.employer.full_name
    r.company_name = job.employer.company_name
    return r


# ── 9. UPDATE JOB ─────────────────────────────────────────────────────────────
@app.put("/jobs/{job_id}", response_model=schemas.JobResponse)
def update_job(job_id: int, data: schemas.JobUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own jobs")

    for field, value in data.dict(exclude_none=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


# ── 10. DELETE JOB ────────────────────────────────────────────────────────────
@app.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own jobs")
    db.delete(job)
    db.commit()


# ── 11. APPLY TO JOB ──────────────────────────────────────────────────────────
@app.post("/applications/", response_model=schemas.ApplicationResponse, status_code=201)
def apply_to_job(data: schemas.ApplicationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "jobseeker":
        raise HTTPException(status_code=403, detail="Only job seekers can apply")

    job = db.query(models.Job).filter(models.Job.id == data.job_id, models.Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or no longer active")

    existing = db.query(models.Application).filter(
        models.Application.job_id == data.job_id,
        models.Application.applicant_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already applied to this job")

    app = models.Application(job_id=data.job_id, applicant_id=current_user.id, cover_letter=data.cover_letter)
    db.add(app)
    db.commit()
    db.refresh(app)

    r = schemas.ApplicationResponse.from_orm(app)
    r.job_title = job.title
    r.applicant_name = current_user.full_name
    return r


# ── 12. MY APPLICATIONS ───────────────────────────────────────────────────────
@app.get("/applications/my", response_model=List[schemas.ApplicationResponse])
def my_applications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    apps = db.query(models.Application).filter(models.Application.applicant_id == current_user.id).all()
    result = []
    for a in apps:
        r = schemas.ApplicationResponse.from_orm(a)
        r.job_title = a.job.title
        r.applicant_name = current_user.full_name
        result.append(r)
    return result


# ── 13. JOB APPLICATIONS (employer) ──────────────────────────────────────────
@app.get("/applications/job/{job_id}", response_model=List[schemas.ApplicationResponse])
def job_applications(job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.Job).filter(models.Job.id == job_id, models.Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not yours")

    apps = db.query(models.Application).filter(models.Application.job_id == job_id).all()
    result = []
    for a in apps:
        r = schemas.ApplicationResponse.from_orm(a)
        r.job_title = job.title
        r.applicant_name = a.applicant.full_name
        result.append(r)
    return result


# ── 14. UPDATE APPLICATION STATUS ────────────────────────────────────────────
@app.put("/applications/{app_id}/status", response_model=schemas.ApplicationResponse)
def update_application_status(app_id: int, data: schemas.ApplicationStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    application = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    valid_statuses = ["Pending", "Reviewed", "Shortlisted", "Rejected"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    application.status = data.status
    db.commit()
    db.refresh(application)
    r = schemas.ApplicationResponse.from_orm(application)
    r.job_title = application.job.title
    r.applicant_name = application.applicant.full_name
    return r


# ── 15. BOOKMARK A JOB ───────────────────────────────────────────────────────
@app.post("/bookmarks/", response_model=schemas.BookmarkResponse, status_code=201)
def bookmark_job(data: schemas.BookmarkCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    existing = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.job_id == data.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Job already bookmarked")

    bm = models.Bookmark(user_id=current_user.id, job_id=data.job_id)
    db.add(bm)
    db.commit()
    db.refresh(bm)
    r = schemas.BookmarkResponse.from_orm(bm)
    r.job_title = bm.job.title
    return r


# ── 16. GET MY BOOKMARKS ─────────────────────────────────────────────────────
@app.get("/bookmarks/my", response_model=List[schemas.BookmarkResponse])
def my_bookmarks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bms = db.query(models.Bookmark).filter(models.Bookmark.user_id == current_user.id).all()
    result = []
    for bm in bms:
        r = schemas.BookmarkResponse.from_orm(bm)
        r.job_title = bm.job.title
        result.append(r)
    return result


# ── 17. DASHBOARD STATS ───────────────────────────────────────────────────────
@app.get("/dashboard/stats", response_model=schemas.DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    return {
        "total_jobs": db.query(models.Job).count(),
        "total_users": db.query(models.User).count(),
        "total_applications": db.query(models.Application).count(),
        "active_jobs": db.query(models.Job).filter(models.Job.is_active == True).count(),
    }


@app.get("/")
def root():
    return {"message": "Job Portal API is running", "docs": "/docs"}
