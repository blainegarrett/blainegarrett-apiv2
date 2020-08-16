# Blog Media Service
import logging
from pydantic import BaseModel
from ..entities import MediaEntity
from ..models import MediaModel
from typing import List, Optional
import logging

from google.cloud import ndb
from core.datastore import get_resource_id_from_key, get_key_from_resource_id
from core.exceptions import DoesNotExistException
from core.datastore import InvalidIdException

client = ndb.Client()

# TODO: Can we leverage generics to do this?
# Does it need to be a model?


class MediaModelPagedResult(BaseModel):
    more: bool
    cursor: str
    models: List[MediaModel]


def map_entity_to_model(e: MediaEntity) -> MediaModel:
    m = MediaModel(
        resource_id=get_resource_id_from_key(e.key),
        content_type=e.content_type,
        gcs_filename=e.gcs_filename,
        size=e.size
    )
    return m


def get_by_id(resource_id: str) -> MediaModel:
    with client.context():
        try:
            key = get_key_from_resource_id(resource_id)
        except InvalidIdException as e:
            raise DoesNotExistException('Invalid key')

        e: Optional[MediaEntity] = key.get()

        if (not e):
            raise DoesNotExistException('Resource Does not Exist')

        # TODO: Write mapper...
        return map_entity_to_model(e)


def get_list(limit: int, cursor: str, sort: str) -> MediaModelPagedResult:
    models: List[MediaModel] = []

    # Query Options
    opts = {}
    if (cursor):
        opts = {'start_cursor': ndb.Cursor(urlsafe=cursor)}

    # Run Query
    with client.context():
        q = MediaEntity.query()
        q = q.order(MediaEntity.gcs_filename)
        [results, nextCursor, more] = q.fetch_page(limit, **opts)

    # Map Results to Domain Model
    models = [map_entity_to_model(e) for e in results]
    return MediaModelPagedResult(models=models, cursor=nextCursor.urlsafe(), more=more)
