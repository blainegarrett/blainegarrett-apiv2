# Blog Categories Service
import logging
from pydantic import BaseModel
from ..entities import CategoryEntity
from ..models import CategoryModel
from typing import List, Optional
import logging

from google.cloud import ndb
from core.datastore import get_resource_id_from_key, get_key_from_resource_id
from core.exceptions import DoesNotExistException
from core.datastore import InvalidIdException

client = ndb.Client()

# TODO: Can we leverage generics to do this?
# Does it need to be a model?


class CategoryModelPagedResult(BaseModel):
    more: bool
    cursor: str
    models: List[CategoryModel]

# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/standard/migration/ndb/overview/main.py


def map_entity_to_model(e: CategoryEntity) -> CategoryModel:
    m = CategoryModel(
        resource_id=get_resource_id_from_key(e.key),
        name=e.name,
        slug=e.slug,
    )
    return m


def get_by_slug(slug: str) -> CategoryModel:
    slug = slug.lower()
    with client.context():
        q = CategoryEntity.query().filter(CategoryEntity.slug == slug)
        e = q.get()
        if (not e):
            raise DoesNotExistException('Resource Does not Exist')
        return map_entity_to_model(e)


def get_by_id(resource_id: str) -> Optional[CategoryModel]:
    with client.context():
        try:
            key = get_key_from_resource_id(resource_id)
        except InvalidIdException as e:
            raise DoesNotExistException('Invalid key')

        e = key.get()

        if (not e):
            raise DoesNotExistException('Resource Does not Exist')

        return map_entity_to_model(e)


def get_list(limit: int, cursor: str, sort: str) -> CategoryModelPagedResult:
    models: List[CategoryModel] = []

    # Query Options
    opts = {}
    if (cursor):
        opts = {'start_cursor': ndb.Cursor(urlsafe=cursor)}

    # Run Query
    with client.context():
        q = CategoryEntity.query()
        q = q.order(CategoryEntity.name)
        [results, nextCursor, more] = q.fetch_page(limit, **opts)

    # Map Results to Domain Model
    models = [map_entity_to_model(e) for e in results]
    return CategoryModelPagedResult(models=models, cursor=nextCursor.urlsafe(), more=more)
