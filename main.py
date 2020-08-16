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

# TODO: Power of environment variables...
origins = ["https://blainegarrett.com"]
orgin_regexp = r'(http.*://www.blainegarrett.com)|(htt.*://blaine-garrett.appspot.com)|http://localhost:.*'

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


@app.get("/api/rest/v2.0/media")
def get_media(limit: int = 10, cursor: str = None, sort: str = 'name'):
    # TODO: Check cache
    # TODO: Error Handling
    # TODO: Sorting Not Implemented

    result = media_service.get_list(limit, cursor or "", sort)
    resources: List[MediaResourceVerbose] = []
    for m in result.models:
        resources.append(create_media_resource(m, True))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


@app.get("/api/rest/v2.0/media/{resource_id}")
def get_category(resource_id):
    m = media_service.get_by_id(resource_id)
    return {'results': create_media_resource(m, True)}


@app.get("/api/rest/v2.0/categories")
def get_categories(limit: int = 10, cursor: str = None, sort: str = 'name', get_by_slug: str = None):
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


@app.get("/api/rest/v2.0/categories/{resource_id}")
def get_category(resource_id):
    m = category_service.get_by_id(resource_id)
    return {'results': create_category_resource(m, True)}


@app.get("/api/rest/v2.0/posts")
def get_categories(category_slug: Optional[str] = None, limit: int = 10, cursor: str = None, sort: str = 'name', get_by_slug: str = None, verbose: bool = False, is_published: bool = True):
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
        # logging.error(m)
        resources.append(create_article_resource(m, verbose))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


@app.get("/api/rest/v2.0/posts/{resource_id}")
def get_article(resource_id):
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
