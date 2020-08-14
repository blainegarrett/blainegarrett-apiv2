# Blog Categories Service
import logging
from pydantic import BaseModel
from ..entities import ArticleEntity
from ..models import ArticleModel
from typing import List, Optional

from google.cloud import ndb
from core.datastore import get_resource_id_from_key, get_key_from_resource_id
from core.exceptions import DoesNotExistException
from core.datastore import InvalidIdException

client = ndb.Client()

# TODO: Can we leverage generics to do this?
# Does it need to be a model?


class ArticleModelPagedResult(BaseModel):
    more: bool
    cursor: str
    models: List[ArticleModel]

# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/standard/migration/ndb/overview/main.py


def map_entity_to_model(e: ArticleEntity) -> ArticleModel:
    m = ArticleModel(
        resource_id=get_resource_id_from_key(e.key),
        title=e.title,
        slug=e.slug,
        content=e.content,
        summary=e.summary,
        is_published=e.is_published,
        created_date=e.created_date,
        modified_date=e.modified_date,
        published_date=e.published_date,
    )
    return m


def get_by_slug(slug: str) -> Optional[ArticleModel]:
    slug = slug.lower()
    with client.context():
        q = ArticleEntity.query().filter(ArticleEntity.slug == slug)
        e = q.get()
        if (not e):
            return None
        return map_entity_to_model(e)


def get_by_id(resource_id: str) -> Optional[ArticleModel]:
    with client.context():
        try:
            key = get_key_from_resource_id(resource_id)
        except InvalidIdException as e:
            raise DoesNotExistException('Invalid key')

        e = key.get()

        if (not e):
            raise DoesNotExistException('Resource Does not Exist')

        return map_entity_to_model(e)


def get_list(limit: int, cursor: str, sort: str) -> ArticleModelPagedResult:
    models: List[ArticleModel] = []

    # Query Options
    opts = {}
    if (cursor):
        opts = {'start_cursor': ndb.Cursor(urlsafe=cursor)}

    # Run Query
    with client.context():
        q = ArticleEntity.query()
        q = q.order(-ArticleEntity.created_date)
        [results, nextCursor, more] = q.fetch_page(limit, **opts)

    # Map Results to Domain Model
    models = [map_entity_to_model(e) for e in results]
    return ArticleModelPagedResult(models=models, cursor=nextCursor.urlsafe(), more=more)
