from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
mail = Mail()
jwt = JWTManager()
cors = CORS()  # 解决跨域问题


def init_ext(app):
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
