
from pydantic import BaseModel


class ResourceMeta(BaseModel):
    resource_id: str
    is_verbose: bool


class Resource(BaseModel):
    _meta: ResourceMeta


class ArticleResource(Resource):
    title: str


class Child(BaseModel):
    name: str

    class Config:
        extra = 'forbid'


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False
