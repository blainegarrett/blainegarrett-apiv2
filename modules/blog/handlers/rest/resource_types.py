# Rest Resource
# TODO: These are REST DAOs, maybe we rename them that

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Auditable(BaseModel):
    created_date: Optional[datetime]
    modified_date: Optional[datetime]


class CategoryResource(BaseModel):
    resource_id: str
    name: str
    slug: str


class MediaResource(BaseModel):
    resource_id: str
    content_type: Optional[str]
    filename: Optional[str]
    gcs_filename: Optional[str]
    size: Optional[int]


class ArticleResource(BaseModel):
    resource_id: str
    slug: str
    title: str
    summary: str
    is_published: bool
    published_date: Optional[datetime]


class ArticleResourceVerbose(ArticleResource, Auditable):
    content: str
