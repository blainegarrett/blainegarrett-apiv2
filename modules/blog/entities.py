# Blog Datastore Entities

from google.cloud import ndb


class CategoryEntity(ndb.Model):  # Move to models
    @classmethod
    def _get_kind(cls):
        return 'BlogCategory'

    name = ndb.StringProperty()
    slug = ndb.StringProperty()


# https://github.com/blainegarrett/blainegarrett-api/blob/1d5ee6de5dc159b352af9183f814c6945437f8d7/app/modules/files/internal/entities.py
class MediaEntity(ndb.Model):
    @classmethod
    def _get_kind(cls):
        return 'BlogMedia'

    content_type = ndb.StringProperty()
    filename = ndb.StringProperty()
    gcs_filename = ndb.StringProperty()
    size = ndb.IntegerProperty()


class ArticleEntity(ndb.Model):
    @classmethod
    def _get_kind(cls):
        return 'BlogPost'

    slug = ndb.StringProperty()
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    summary = ndb.StringProperty(default="")
    is_published = ndb.BooleanProperty(default=False)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    modified_date = ndb.DateTimeProperty(auto_now=True)
    published_date = ndb.DateTimeProperty(indexed=True)
    categories = ndb.KeyProperty(repeated=True)
    primary_media_image = ndb.KeyProperty(kind=MediaEntity)
