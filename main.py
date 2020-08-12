from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, escape, request

from core import Item, ArticleResource, ResourceMeta
flask_app = Flask(__name__)


@flask_app.route('/')
def flask_main():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)} from Flask!"


app = FastAPI()


@app.get("/v2")
def read_main():
    a = ArticleResource(title='Party')
    # a._meta = ResourceMeta(is_verbose=True, resource_id='asdf444')
    a.title = 'Tacos'

    # i: Item = Item(name='sdsxxssf', price=43)
    # i.is_offer = False

    return a
    return {"message": "Hello World"}


app.mount("/v1", WSGIMiddleware(flask_app))
