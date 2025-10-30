from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Article(BaseModel):
    id: int
    source: str                 # "CNN" | "BBC" | "FOX"
    title: str
    url: str
    content: str                # raw/cleaned text
    created_at: datetime

class ArticleCreate(BaseModel):
    source: str
    title: str
    url: str
    content: str

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class EmailRecipient(BaseModel):
    name: Optional[str] = None
    email: EmailStr

class ScheduleRequest(BaseModel):
    subject: str
    body_template: str          # e.g. "Top headlines:\n{headlines}"
    cron: Optional[str] = None  # "*/30 * * * *" or None for one-shot
