from typing import Dict, Generic, TypeVar, Optional, List
from flask import Flask, escape, request
from typing import Generic, List, Any
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware

from pydantic import BaseModel
from pydantic.generics import GenericModel
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from modules.blog.services import category_service
from modules.blog.services import media_service
from modules.blog.services import article_service

from core.exceptions import DoesNotExistException
from modules.blog.handlers.rest.resource_types import CategoryResource
from modules.blog.handlers.rest.resource_types import MediaResource
from modules.blog.handlers.rest.resource_types import ArticleResource, ArticleResourceVerbose

flask_app = Flask(__name__)
app = FastAPI()


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


@ app.get("/api/rest/v2.0/media")
def get_media(limit: int = 10, cursor: str = None, sort: str = 'name'):
    # TODO: Check cache
    # TODO: Error Handling
    # TODO: Sorting Not Implemented

    result = media_service.get_list(limit, cursor or "", sort)
    resources: List[MediaResource] = []
    for m in result.models:
        resources.append(MediaResource(
            resource_id=m.resource_id,
            content_type=m.content_type,
            filename=m.filename,
            gcs_filename=m.gcs_filename,
            size=m.size,
        ))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


@ app.get("/api/rest/v2.0/media/{resource_id}")
def get_category(resource_id):
    m = media_service.get_by_id(resource_id)
    return {'results': MediaResource(
            resource_id=m.resource_id,
            content_type=m.content_type,
            filename=m.filename,
            gcs_filename=m.gcs_filename,
            size=m.size,
            )}


@ app.get("/api/rest/v2.0/categories")
def get_categories(limit: int = 10, cursor: str = None, sort: str = 'name', get_by_slug: str = None):
    # TODO: Check cache
    # TODO: Error Handling
    # TODO: Sorting Not Implemented

    if (get_by_slug):
        m = category_service.get_by_slug(get_by_slug)
        if (m):
            return {'results': CategoryResource(
                resource_id=m.resource_id, name=m.name, slug=m.slug)}
        else:
            raise DoesNotExistException(
                f"Resource given by slug '{get_by_slug}' Not Found")

    result = category_service.get_list(limit, cursor or "", sort)
    resources: List[CategoryResource] = []
    for m in result.models:
        resources.append(CategoryResource(
            resource_id=m.resource_id, name=m.name, slug=m.slug))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


@ app.get("/api/rest/v2.0/categories/{resource_id}")
def get_category(resource_id):
    m = category_service.get_by_id(resource_id)
    return {'results': CategoryResource(
            resource_id=m.resource_id, name=m.name, slug=m.slug)}


@ app.get("/api/rest/v2.0/posts")
def get_categories(limit: int = 10, cursor: str = None, sort: str = 'name', get_by_slug: str = None, is_verbose: bool = False):
    # TODO: Check cache
    # TODO: Error Handling
    # TODO: Sorting Not Implemented

    if (get_by_slug):
        m = article_service.get_by_slug(get_by_slug)
        if (m):
            return {'results': ArticleResource(
                resource_id=m.resource_id, name=m.name, slug=m.slug)}
        else:
            raise DoesNotExistException(
                f"Resource given by slug '{get_by_slug}' Not Found")

    responseClass = ArticleResource
    if (is_verbose):
        responseClass = ArticleResourceVerbose

    result = article_service.get_list(limit, cursor or "", sort)
    resources: List[ArticleResource] = []
    for m in result.models:
        resources.append(responseClass(
            resource_id=m.resource_id,
            slug=m.slug or '',
            title=m.title or '',
            content=m.content or '',
            summary=m.summary or '',
            is_published=m.is_published or False,
            created_date=m.created_date,
            modified_date=m.modified_date,
            published_date=m.published_date,
        ))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


@ app.get("/api/rest/v2.0/posts/{resource_id}",
          # response_class=Response[ArticleResourceVerbose]
          )
def get_category(resource_id):
    m = article_service.get_by_id(resource_id)
    r: ArticleResourceVerbose = ArticleResourceVerbose(
        resource_id=m.resource_id,
        slug=m.slug or '',
        title=m.title or '',
        content=m.content or '',
        summary=m.summary or '',
        is_published=m.is_published or False,
        created_date=m.created_date,
        modified_date=m.modified_date,
        published_date=m.published_date,
    )
    return Response[ArticleResourceVerbose](results=r)


app.mount("/api/rest/v2.0", WSGIMiddleware(flask_app))
