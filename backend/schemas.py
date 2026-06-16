from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── AUTH ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # jobseeker or employer
    company_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int


# ── USER ─────────────────────────────────────────────────────────────────────

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    company_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    bio: Optional[str]
    skills: Optional[str]
    company_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── JOB ──────────────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    description: str
    category: str
    location: str
    job_type: str
    salary_range: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    is_active: Optional[bool] = None

class JobResponse(BaseModel):
    id: int
    employer_id: int
    title: str
    description: str
    category: str
    location: str
    job_type: str
    salary_range: Optional[str]
    is_active: bool
    created_at: datetime
    employer_name: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        from_attributes = True


# ── APPLICATION ───────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None

class ApplicationStatusUpdate(BaseModel):
    status: str  # Pending, Reviewed, Shortlisted, Rejected

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    cover_letter: Optional[str]
    status: str
    applied_at: datetime
    job_title: Optional[str] = None
    applicant_name: Optional[str] = None

    class Config:
        from_attributes = True


# ── BOOKMARK ──────────────────────────────────────────────────────────────────

class BookmarkCreate(BaseModel):
    job_id: int

class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    saved_at: datetime
    job_title: Optional[str] = None

    class Config:
        from_attributes = True


# ── DASHBOARD ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_jobs: int
    total_users: int
    total_applications: int
    active_jobs: int
