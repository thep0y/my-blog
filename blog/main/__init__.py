from flask import Flask, g

from main.ext import init_ext
from main.views import init_view


def create_app(env):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(env)
    init_view(app)
    init_ext(app)

    return app
