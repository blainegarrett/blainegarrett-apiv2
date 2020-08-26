# Blog Categories Service
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import ndb

from core.datastore import get_resource_id_from_key, get_key_from_resource_id
from core.exceptions import DoesNotExistException
from core.datastore import InvalidIdException
from modules.blog.services.media_service import map_entity_to_model as media_map
from ..entities import ArticleEntity
from ..models import ArticleModel


client = ndb.Client()

# TODO: Can we leverage generics to do this?
# Does it need to be a model?


class ArticleModelPagedResult(BaseModel):
    more: bool
    cursor: str
    models: List[ArticleModel]

# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/standard/migration/ndb/overview/main.py


LEGACY_IMAGE_PROP = 'LEGACY_IMAGE_PROP'


def bulk_dereference(entities: List[ArticleEntity]) -> List[ArticleEntity]:

    # Step 1: Collect Ids
    entity_map = {}
    return_entities = []
    for e in entities:
        setattr(e, LEGACY_IMAGE_PROP, None)

        # Legacy image - it is a ndb key property
        if e.primary_media_image:
            entity_map[e.primary_media_image] = None

    # Step 2: Fetch all of the entities we want to deref
    subentities = ndb.get_multi(entity_map.keys())

    for se in subentities:
        if (se):
            entity_map[se.key] = se

    # Step 3: Iterate over posts and link up the dereferenced props
    for e in entities:
        if e.primary_media_image:
            se = entity_map.get(
                e.primary_media_image, None)
            setattr(e, LEGACY_IMAGE_PROP, se)

        return_entities.append(e)
    return return_entities


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
        published_date=e.published_date
    )

    if (e.primary_media_image):
        m.legacy_image_resource_id = get_resource_id_from_key(
            e.primary_media_image)

    if (hasattr(e, LEGACY_IMAGE_PROP)):

        bulk_dereferenced_media_entity = getattr(e, LEGACY_IMAGE_PROP, None)
        if (bulk_dereferenced_media_entity):
            m.legacy_image_resource = media_map(bulk_dereferenced_media_entity)

    return m


def get_by_slug(slug: str) -> Optional[ArticleModel]:
    slug = slug.lower()
    with client.context():
        q = ArticleEntity.query().filter(ArticleEntity.slug == slug)
        e = q.get()
        if (not e):
            return None
        return map_entity_to_model(bulk_dereference([e])[0])


def get_by_id(resource_id: str) -> ArticleModel:
    with client.context():
        try:
            key = get_key_from_resource_id(resource_id)
        except InvalidIdException as e:
            raise DoesNotExistException('Invalid key')

        e = key.get()

        if (not e):
            raise DoesNotExistException('Resource Does not Exist')

        return map_entity_to_model(bulk_dereference([e])[0])


def get_list(limit: int, cursor: str, sort: str, is_published: bool, category_resource_id: Optional[str]) -> ArticleModelPagedResult:
    models: List[ArticleModel] = []

    # Query Options
    opts = {}
    if (cursor):
        opts = {'start_cursor': ndb.Cursor(urlsafe=cursor)}

    # Run Query
    with client.context():
        q = ArticleEntity.query()
        q = q.filter(ArticleEntity.is_published == is_published)

        # If there is a category resource_id, filter by it
        if (category_resource_id):
            category_key = get_key_from_resource_id(category_resource_id)
            q = q.filter(ArticleEntity.categories == category_key)

        # TODO: Support custom sorting... requires some additional indexes...
        q = q.order(-ArticleEntity.published_date)

        [results, nextCursor, more] = q.fetch_page(limit, **opts)

        # Bulk Dereference Entities
        derefenced_entities = bulk_dereference(results)
        # [logging.error(getattr(e, LEGACY_IMAGE_PROP, None)) for e in derefenced_entities]

        # Map Results to Domain Model
        models = [map_entity_to_model(e) for e in derefenced_entities]
    return ArticleModelPagedResult(models=models, cursor=nextCursor.urlsafe(), more=more)
