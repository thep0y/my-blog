# -*- coding: utf-8 -*-
import os

from flask import request, jsonify
from flask_script import Manager
from flask_migrate import MigrateCommand

from main import create_app
from main.models.blog.blog_model import BlockedIPModel
from main.settings import envs

env = os.environ.get('FLASK_ENV') or 'default'
app = create_app(envs.get(env))
manage = Manager(app)
manage.add_command('db', MigrateCommand)

@app.before_request
def check_ip():
    ip = request.remote_addr
    ip_ = BlockedIPModel.query.filter_by(ip=ip).first()
    if ip_:
        return jsonify({'error': '当前ip已被封禁'}), 403


if __name__ == '__main__':
    manage.run()
