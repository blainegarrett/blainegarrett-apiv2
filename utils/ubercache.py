# TODO: This needs cleanup and tests and review...

import logging
from datetime import timedelta
from datetime import datetime
from typing import List  # Note: This is mocked specifically in testing
import redis
from google.cloud import ndb
import os


class Client:
    """
    Singleton Object to ensure we only use one instance per request
    """
    ndb_client = None
    redis_client = None

    def __init__(self):
        if not Client.ndb_client:
            Client.ndb_client = ndb.Client()

        logging.error(os.environ.get('REDIS_HOST'))

        if not Client.redis_client:
            redis_host = os.environ.get('REDIS_HOST', 'localhost')
            redis_port = int(os.environ.get('REDIS_PORT', 6666))
            redis_password = os.environ.get('REDIS_PASSWORD', '')

            redis_args = {'host': redis_host, 'port': redis_port}

            if (bool(redis_password)):
                redis_args['password'] = redis_password

            Client.redis_client = redis.StrictRedis(
                decode_responses=True, **redis_args)


def cache_set(key, value, time=None, category=None, write_entity=True):
    """
    """
    client = Client()

    if write_entity:
        now = datetime.now()

        expiration_date = None

        if time:
            delta = timedelta(seconds=time)
            expiration_date = now + delta

        if not category:
            category = []

        if category and not isinstance(category, list):
            category = [category]

        with client.ndb_client.context():
            ds_key = ndb.Key('MemcacheEntity', key)
            e = MemcacheEntity(key=ds_key,
                               value=value,
                               expiration_time=time,
                               expires=expiration_date,
                               category=category)
            future = e.put_async(use_memcache=False)

            # Setup memcache operation
            # , time) TODO: Get expiration working..
            memcached_return_value = client.redis_client.set(key, value)

            # Get async value
            if write_entity:
                db_key_put = future.get_result()

    return True


def cache_delete_all():
    client = Client()
    with client.ndb_client.context():
        future = MemcacheEntity.query().fetch_async(
            keys_only=True, use_memcache=False)

        result = future.get_result()

        ds_keys_to_delete = []
        memcache_keys_to_delete: List[str] = []

        for ds_key in result:
            ds_keys_to_delete.append(ds_key)
            memcache_keys_to_delete.append(ds_key.id())

        # Delete datastore entites
        ndb.delete_multi(ds_keys_to_delete)
        # for k in memcache_keys_to_delete:
        #    client.redis_client.delete(k)
        # memcache.delete_multi(memcache_keys_to_delete)
        client.redis_client.flushall()

    return memcache_keys_to_delete  # Return a list of keys that were deleted


def cache_delete(key):
    """
    """
    client = Client()

    ds_key = ndb.Key('MemcacheEntity', key)
    future = ds_key.delete_async(use_memcache=False)
    client.redis_client.delete(key)
    future.get_result()

    return True


def cache_get(key):
    """
    Retrieve an item from the cache
    """
    client = Client()

    # Check if in memcache
    value = client.redis_client.get(key)
    if value:
        return value

    with client.ndb_client.context():
        # else, check datastore backup
        ds_key = ndb.Key('MemcacheEntity', key)
        ds_entity = ds_key.get()

    if not ds_entity:
        return None

    logging.debug(
        'Memcache miss for key %s, but there is a datastore entity.' % key)
    expiration = ds_entity.expires
    value = ds_entity.value

    if expiration and expiration < datetime.now():
        return None  # value is stale, could should would delete the db Entity

    # Update memcache value since it was a miss...
    cache_set(key, value, ds_entity.expiration_time, write_entity=False)

    return value


def cache_invalidate(category):
    """
    Given a category, invalidate all items with this category
    """
    client = Client()

    with client.ndb_client.context():
        future = MemcacheEntity.query(MemcacheEntity.category == category).fetch_async(
            keys_only=True, use_memcache=False)

        result = future.get_result()

        ds_keys_to_delete = []
        memcache_keys_to_delete: List[str] = []

        for ds_key in result:
            ds_keys_to_delete.append(ds_key)
            memcache_keys_to_delete.append(ds_key.id())

        # Delete datastore entites
        ndb.delete_multi(ds_keys_to_delete)
        for k in memcache_keys_to_delete:
            client.redis_client.delete(k)
        # memcache.delete_multi(memcache_keys_to_delete)

    return memcache_keys_to_delete  # Return a list of keys that were deleted


class MemcacheEntity(ndb.Model):
    """
    A lightweight entity to function as a memcache backup in systems where
    memcache keys don't exisit in pool very long due to overuse.

    datastore entity key is itself the memcache key.
    """

    value = ndb.PickleProperty()
    created_date = ndb.DateTimeProperty(auto_now=True)
    # The `time` value you would pass to memcache.set
    expiration_time = ndb.IntegerProperty()
    # Created timestamp + the expiration time for easy querying
    expires = ndb.DateTimeProperty()
    category = ndb.StringProperty(indexed=True, repeated=True)
