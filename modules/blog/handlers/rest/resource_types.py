# Rest Resource
# TODO: These are REST DAOs, maybe we rename them that

from pydantic import BaseModel


class CategoryResource(BaseModel):
    resource_id: str
    name: str
    slug: str
