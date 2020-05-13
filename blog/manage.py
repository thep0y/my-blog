# -*- coding: utf-8 -*-
import os

from flask_script import Manager
from flask_migrate import MigrateCommand

from main import create_app
from main.settings import envs

env = os.environ.get('FLASK_ENV') or 'default'
app = create_app(envs.get(env))
manage = Manager(app)
manage.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manage.run()
