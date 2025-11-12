"""
Database Schemas for the Marketing site

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).

Collections created here:
- Lead -> "lead": contact/lead submissions
- Service -> "service": list of services offered (IT and Satcom)
- CaseStudy -> "casestudy": case studies/portfolio items
- NewsItem -> "newsitem": recent updates/news highlights
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

class Lead(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company name")
    service_interest: Optional[str] = Field(None, description="Interested service or category")
    message: Optional[str] = Field(None, description="Message from the lead")
    source: Optional[str] = Field("website", description="Where this lead originated")

class Service(BaseModel):
    title: str = Field(..., description="Service title")
    category: Literal["IT", "Satcom"] = Field(..., description="Service category")
    description: str = Field(..., description="Short description")
    features: List[str] = Field(default_factory=list, description="Key features/bullets")
    icon: Optional[str] = Field(None, description="Icon name for UI (lucide icon key)")

class CaseStudy(BaseModel):
    title: str = Field(..., description="Case study title")
    client: str = Field(..., description="Client name")
    industry: Optional[str] = Field(None, description="Industry/vertical")
    summary: str = Field(..., description="Short summary of the engagement")
    results: List[str] = Field(default_factory=list, description="Measurable results/outcomes")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")
    featured_image: Optional[str] = Field(None, description="Hero/cover image URL")

class NewsItem(BaseModel):
    title: str = Field(..., description="News title")
    summary: str = Field(..., description="Short summary")
    url: Optional[str] = Field(None, description="Link for more details")
    published_at: datetime = Field(default_factory=datetime.utcnow, description="Publish timestamp")
