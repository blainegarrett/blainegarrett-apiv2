from flask import Flask, escape, request
from typing import List
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware

from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from modules.blog.services import category_service
from core.exceptions import DoesNotExistException
from modules.blog.handlers.rest.resource_types import CategoryResource

flask_app = Flask(__name__)
app = FastAPI()


@flask_app.route('/')
def flask_main():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)} from Flask!"

# Register Exception Handlers


@app.exception_handler(Exception)
async def v2_generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "messages": [f"{exc}"], }
    )


@app.exception_handler(DoesNotExistException)
async def v2_404_exception_handler(request: Request, exc: DoesNotExistException):
    return JSONResponse(
        status_code=404,
        content={
            "status": 404,
            "messages": [f"{exc}"], }
    )


@app.get("/api/rest/v2.0/categories")
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

    result = category_service.get_categories(limit, cursor or "", sort)
    resources: List[CategoryResource] = []
    for m in result.models:
        resources.append(CategoryResource(
            resource_id=m.resource_id, name=m.name, slug=m.slug))

    return {'results': resources, 'more': result.more, 'cursor': result.cursor}


@app.get("/api/rest/v2.0/categories/{resource_id}")
def get_category(resource_id):
    m = category_service.get_by_id(resource_id)
    return {'results': CategoryResource(
            resource_id=m.resource_id, name=m.name, slug=m.slug)}


app.mount("/api/rest/v2.0", WSGIMiddleware(flask_app))
