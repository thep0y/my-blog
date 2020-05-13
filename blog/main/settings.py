# 本settings用不上，生效的settings全在blog_api的settings里

import os
import platform
from datetime import timedelta

current_os = platform.platform()

SERVER_HOST = 'http://127.0.0.1:5000/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'Blog测试'
if 'Linux' in current_os:
    MYSQL_HOST = '172.17.0.2'
    REDIS_HOST = '172.17.0.3:6379'
elif 'Darwin' in current_os:
    REDIS_HOST = '192.168.2.128:6379'
    MYSQL_HOST = '192.168.2.128'


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'qwertyuiopasdfgh'  # It must be 16, 24 or 32 bytes long

    # JWT
    # JWT_ACCESS_TOKEN_EXPIRES = 60*60*24
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=31)

    # Cache
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'cache:'
    CACHE_REDIS_URL = f'redis://{REDIS_HOST}'  # redis和mysql都用的docker，改成自己的真实地址


def get_db_uri(db_info):
    # 如果没有设置数据库，就默认用sqlite
    engine = db_info.get('ENGINE', 'sqlite')
    driver = db_info.get('DRIVER', '')
    user = db_info.get('USER', '')
    password = db_info.get('PASSWORD', '')
    host = db_info.get('HOST', '')
    port = db_info.get('PORT', '')
    try:
        name = db_info['NAME']
        if engine == 'sqlite':
            uri = f'sqlite:///{name}'
        else:
            uri = f'{engine}+{driver}://{user}:{password}@{host}:{port}/{name}?charset=UTF8MB4'
        return uri
    except KeyError:
        raise KeyError('你没有指定数据库，请检查setting.py中的config参数')


class DevelopmentConfig(Config):
    DEBUG = True
    db_info = {
        'ENGINE': 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': '000aaa',
        'HOST': MYSQL_HOST,
        'PORT': 3306,
        'NAME': 'blog'
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


class TestingConfig(Config):
    TESTING = True
    db_info = {
        'ENGINE': 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 3306,
        'NAME': 'user'
    }
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


class StagingConfig(Config):
    db_info = {
        'ENGINE': 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 3306,
        'NAME': 'users'
    }
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


class ProductionConfig(Config):
    db_info = {
        'ENGINE': 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 3306,
        'NAME': 'restful'
    }
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


envs = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}

