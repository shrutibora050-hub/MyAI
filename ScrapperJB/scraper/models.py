from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class JobPosting(BaseModel):
    """Model for a job posting"""
    title: str
    company: str
    location: str
    job_url: str
    description: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    category: Optional[str] = None
    posted_date: Optional[str] = None
    scraped_at: datetime = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
