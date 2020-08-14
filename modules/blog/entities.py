# Blog Datastore Entities

from google.cloud import ndb


class CategoryEntity(ndb.Model):  # Move to models
    @classmethod
    def _get_kind(cls):
        return 'BlogCategory'

    name = ndb.StringProperty()
    slug = ndb.StringProperty()


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
    summary = ndb.StringProperty()
    is_published = ndb.BooleanProperty()
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    modified_date = ndb.DateTimeProperty(auto_now=True)
    published_date = ndb.DateTimeProperty(indexed=True)
