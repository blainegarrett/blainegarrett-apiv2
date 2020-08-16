# Rest Resource
# TODO: These are REST DAOs, maybe we rename them that

from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime
from modules.blog.models import ArticleModel


class Auditable(BaseModel):
    created_date: Optional[datetime]
    modified_date: Optional[datetime]


class Meta(BaseModel):
    resource_id: str
    resource_type: str
    is_verbose: bool


class BaseResource(BaseModel):
    meta: Meta = Field(alias='_meta')


class CategoryResourceVerbose(BaseResource):
    resource_id: str
    name: str
    slug: str


class MediaResourceVerbose(BaseResource):
    resource_id: str
    content_type: Optional[str]
    filename: Optional[str]
    gcs_filename: Optional[str]
    size: Optional[int]


class ArticleResource(BaseResource):
    resource_id: str
    slug: str
    title: str
    summary: str
    is_published: bool
    published_date: Optional[datetime]
    legacy_image_resource: Optional[MediaResourceVerbose]  # image url fragment


class ArticleResourceVerbose(ArticleResource, Auditable):
    content: str


TArticleResource = Union[ArticleResourceVerbose, ArticleResource]
