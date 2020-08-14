# Domain Models
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CategoryModel(BaseModel):
    resource_id: str
    name: str
    slug: str


class MediaModel(BaseModel):
    resource_id: str
    content_type: Optional[str]
    filename: Optional[str]
    gcs_filename: Optional[str]
    size: Optional[int]


class ArticleModel(BaseModel):
    resource_id: str
    slug: Optional[str]
    title: str
    content: Optional[str]
    summary: Optional[str]
    is_published: Optional[bool]
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
    published_date: Optional[datetime]
