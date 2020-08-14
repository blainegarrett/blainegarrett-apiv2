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
