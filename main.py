import json
import logging
import functools
from dotenv import load_dotenv

from fastapi.encoders import jsonable_encoder
from fastapi.responses import UJSONResponse
from json import dumps
from flask import Flask, escape, request
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic.generics import GenericModel
from typing import Dict, Generic, TypeVar, Optional, List
from typing import Generic, List

from core.exceptions import DoesNotExistException
from modules.blog.services import category_service
from modules.blog.services import media_service
from modules.blog.services import article_service
from modules.blog.handlers.rest.resource_types import CategoryResourceVerbose
from modules.blog.handlers.rest.resource_types import MediaResourceVerbose
from modules.blog.handlers.rest.resource_types import ArticleResource, ArticleResourceVerbose, TArticleResource
from modules.blog.models import ArticleModel, CategoryModel, MediaModel
from utils import ubercache

load_dotenv()


# TODO: Power of environment variables...
origins = ["https://blainegarrett.com"]
orgin_regexp = r'(http.*://www.blainegarrett.com)|(http.*://blaine-garrett.appspot.com)|(.*vercel.app)|http://localhost:.*'

flask_app = Flask(__name__)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=orgin_regexp,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DataT = TypeVar('DataT')


class Response(GenericModel, Generic[DataT]):
    results: DataT
    messages: Optional[List[str]] = []
    status: Optional[int] = 200


@flask_app.route('/')
def flask_main():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)} from Flask!"

# Register Exception Handlers


@app.exception_handler(Exception)
async def v2_generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=Response[Dict](
            results={},
            status=500,
            messages=[f"{exc}"]
        ).dict()
    )


@app.exception_handler(DoesNotExistException)
async def v2_404_exception_handler(request: Request, exc: DoesNotExistException):
    return JSONResponse(
        status_code=404,
        content=Response[Dict](
            results={},
            status=404,
            messages=[f"{exc}"]
        ).dict()
    )


@app.get('/redis/flush/all')
def redisTests():
    deleted_keys = ubercache.cache_delete_all()
    return deleted_keys

#     os.environ.get('REDIS_HOST', 'localhost')
#     redis_host = os.environ.get('REDIS_HOST', 'localhost')
#     redis_port = int(os.environ.get('REDIS_PORT', 6666))
#     redis_password = ''

#     import logging
#     redis_client = redis.StrictRedis(decode_responses=True,
#                                      host=redis_host, port=redis_port)

#     logging.error('-------------------------')
#     # logging.error(redis_client.delete('counterx'))
#     logging.error(redis_client.get('counterx'))

#     cache_val: str = ubercache.cache_get('counterx')
#     if (not cache_val):
#         counter = 999
#     else:
#         counter = int(cache_val)
#     ubercache.cache_set('counterx', counter + 1, 30, 'counters')

#     # ubercache.cache_invalidate('counters')

#     # redis_client.delete('counter')
#     # redis_client.flushall()
#     # redis_client.delete("asdfs")
#     midnight_cst = 6000
#     value = redis_client.incr(0)
#     #redis_client.set("asdfs", "sdf", ex=midnight_cst)
#     # key = ''.join(choice(ascii_uppercase) for i in range(30))
#     # val = ''.join(choice(ascii_uppercase) for i in range(30))
#     # value = redis_client.set(key, val)
#     # value = redis_client.set(key + "d", val)
#     # value = redis_client.set(key + "c", val)
#     # value = redis_client.set(key + "b", val)
#     # value = redis_client.set(key + "a", val)

#     return 'Value is' + str(counter)


def create_param_hash(**kwargs) -> str:
    import json
    import hashlib
    string = json.dumps(kwargs, sort_keys=True)

    m = hashlib.sha224(string.encode())
    return m.hexdigest()


def coolcache(path):
    def decr(f):
        @app.get(path)
        @functools.wraps(f)
        def html(request: Request, *args, **kwargs):
            key = create_request_key(path, request)
            cached_val = ubercache.cache_get(key)
            if (cached_val):
                decoded_resp = json.loads(cached_val)
                # logging.error('Cache hit!!!!' + path)
                return decoded_resp

            # logging.error('Cache miss' + path)
            resp = f(request, *args, **kwargs)
            encoded_payload = jsonable_encoder(resp)
            encoded_str = json.dumps(encoded_payload)
            ubercache.cache_set(key, encoded_str)
            return resp
    return decr


# @app.get("/api/rest/v2.0/media")
@coolcache("/api/rest/v2.0/media")
def get_media(request: Request, limit: int = 10, cursor: str = None, sort: str = 'name'):
    # TODO: Check cache
    # TODO: Error Handling
    # TODO: Sorting Not Implemented

    result = media_service.get_list(limit, cursor or "", sort)
    resources: List[MediaResourceVerbose] = []
    for m in result.models:
        resources.append(create_media_resource(m, True))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


# @app.get("/api/rest/v2.0/media/{resource_id}")
@coolcache("/api/rest/v2.0/media/{resource_id}")
def get_category(request: Request, resource_id):
    m = media_service.get_by_id(resource_id)
    return {'results': create_media_resource(m, True)}


@coolcache("/api/rest/v2.0/categories")
# @app.get("/api/rest/v2.0/categories")
def get_categories(request: Request, limit: int = 10, cursor: str = None, sort: str = 'name', get_by_slug: str = None):
    # TODO: Check cache
    # TODO: Error Handling
    # TODO: Sorting Not Implemented

    if (get_by_slug):
        m = category_service.get_by_slug(get_by_slug)
        if (m):
            return {'results': create_category_resource(m, True)}
        else:
            raise DoesNotExistException(
                f"Resource given by slug '{get_by_slug}' Not Found")

    result = category_service.get_list(limit, cursor or "", sort)
    resources: List[CategoryResourceVerbose] = []
    for m in result.models:
        resources.append(create_category_resource(m, True))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


# @app.get("/api/rest/v2.0/categories/{resource_id}")
@coolcache("/api/rest/v2.0/categories/{resource_id}")
def get_category(request: Request, resource_id):
    m = category_service.get_by_id(resource_id)
    return {'results': create_category_resource(m, True)}


def create_request_key(prefix: str, request: Request):
    dict1 = request.query_params.__dict__.get('_dict', {})
    dict2 = request.path_params
    suffix = create_param_hash(**{**dict1, **dict2})
    return "{}:{}".format(prefix, suffix)


# @app.get("/api/rest/v2.0/posts")
@coolcache("/api/rest/v2.0/posts")
def get_posts(request: Request, category_slug: Optional[str] = None, limit: int = 10, cursor: str = None, sort: str = 'name', get_by_slug: str = None, verbose: bool = False, is_published: bool = True):
    # TODO: Check cache
    # TODO: Error Handling
    # TODO: Sorting Not Implemented

    if (get_by_slug):
        m = article_service.get_by_slug(get_by_slug)
        if (m):
            return {'results': create_article_resource(m, verbose)}
        else:
            raise DoesNotExistException(
                f"Resource given by slug '{get_by_slug}' Not Found")

    # Resolve Category Resource Id
    category_resource_id: Optional[str] = None
    if (category_slug):
        category_model = category_service.get_by_slug(category_slug)
        if (not category_model):
            raise DoesNotExistException(
                f"Category with slug '{category_slug}' Not Found")
        category_resource_id = category_model.resource_id

    result = article_service.get_list(
        limit, cursor or "", sort, is_published, category_resource_id)
    resources: List[ArticleResource] = []
    for m in result.models:
        resources.append(create_article_resource(m, verbose))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


# @app.get("/api/rest/v2.0/posts/{resource_id}")
@coolcache("/api/rest/v2.0/posts/{resource_id}")
def get_article(request: Request, resource_id):
    m: ArticleModel = article_service.get_by_id(resource_id)
    r: ArticleResource = create_article_resource(m, verbose=True)
    return Response[TArticleResource](results=r)


def create_article_resource(m: ArticleModel,  verbose=False) -> TArticleResource:
    meta = {
        'resource_type': 'BlogPost',
        'resource_id': m.resource_id,
        'is_verbose': verbose
    }

    resource_class = ArticleResource
    if (verbose):
        resource_class = ArticleResourceVerbose

    # This assumes the Domain model is idential to the Verbose Resource
    fields = m.dict()
    if (m.legacy_image_resource):
        fields['legacy_image_resource'] = create_media_resource(
            m.legacy_image_resource, True)

    return resource_class(_meta=meta, **fields)


def create_media_resource(m: MediaModel,  verbose=False) -> MediaResourceVerbose:
    meta = {
        'resource_type': 'BlogMedia',
        'resource_id': m.resource_id,
        'is_verbose': True
    }

    # This assumes the Domain model is idential to the Verbose Resource
    return MediaResourceVerbose(_meta=meta, **m.dict())


def create_category_resource(m: CategoryModel,  verbose=False) -> CategoryResourceVerbose:
    meta = {
        'resource_type': 'BlogCategory',
        'resource_id': m.resource_id,
        'is_verbose': True
    }

    # This assumes the Domain model is idential to the Verbose Resource
    return CategoryResourceVerbose(_meta=meta, **m.dict())


app.mount("/api/rest/v2.0", WSGIMiddleware(flask_app))
