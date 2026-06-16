from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # jobseeker or employer
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    company_name = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    jobs = relationship("Job", back_populates="employer", cascade="all, delete")
    applications = relationship("Application", back_populates="applicant", cascade="all, delete")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(80), nullable=False)
    location = Column(String(100), nullable=False)
    job_type = Column(String(50), nullable=False)
    salary_range = Column(String(80), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    employer = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete")
    bookmarks = relationship("Bookmark", back_populates="job", cascade="all, delete")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cover_letter = Column(Text, nullable=True)
    status = Column(String(30), default="Pending")
    applied_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (UniqueConstraint("job_id", "applicant_id", name="unique_application"),)

    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "job_id", name="unique_bookmark"),)

    user = relationship("User", back_populates="bookmarks")
    job = relationship("Job", back_populates="bookmarks")
