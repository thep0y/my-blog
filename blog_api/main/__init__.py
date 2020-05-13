from flask import Flask

from main.apis import init_api
from main.ext import init_ext
from middlewares import load_middleware


def create_app(env):
    app = Flask(__name__)
    app.config.from_object(env)
    init_ext(app)
    init_api(app)

    return app
