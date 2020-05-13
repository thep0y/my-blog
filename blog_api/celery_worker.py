from main.settings import celery
from manage import app

celery.conf.update(app.config)
app.app_context().push()