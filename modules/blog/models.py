# Domain Models

from pydantic import BaseModel


class CategoryModel(BaseModel):
    resource_id: str
    name: str
    slug: str
