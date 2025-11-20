"""
Database Schemas for Culinary Educational Website

Each Pydantic model maps to a MongoDB collection (lowercased class name).
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr

class Recipe(BaseModel):
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Short description")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredients")
    steps: List[str] = Field(default_factory=list, description="Preparation steps")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering/search")
    image_url: Optional[HttpUrl] = Field(None, description="Optional image URL")
    video_url: Optional[HttpUrl] = Field(None, description="Optional video URL")

class Lesson(BaseModel):
    title: str = Field(..., description="Lesson title")
    content: str = Field(..., description="Teaching content or summary")
    level: Optional[str] = Field(None, description="Beginner/Intermediate/Advanced")
    tags: List[str] = Field(default_factory=list)
    video_url: Optional[HttpUrl] = Field(None)

class Ad(BaseModel):
    title: str = Field(..., description="Ad headline")
    body: Optional[str] = Field(None, description="Ad copy")
    image_url: Optional[HttpUrl] = Field(None)
    link_url: Optional[HttpUrl] = Field(None)
    active: bool = Field(default=True)

class Video(BaseModel):
    title: str = Field(...)
    description: Optional[str] = Field(None)
    video_url: HttpUrl = Field(..., description="Hosted video URL (YouTube, Vimeo, etc.)")
    tags: List[str] = Field(default_factory=list)

class Contact(BaseModel):
    phone: str = Field(..., description="Contact phone number")
    email: EmailStr = Field(..., description="Contact email")
    address: str = Field(..., description="Physical address")
