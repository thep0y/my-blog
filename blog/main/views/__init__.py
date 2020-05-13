from main.views.api import blue


def init_view(app):
    app.register_blueprint(blue)