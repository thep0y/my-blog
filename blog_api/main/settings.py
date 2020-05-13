import os
import platform
from datetime import timedelta

from celery import Celery

current_os = platform.platform()

SERVER_HOST = '<your server host>'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = '<server host name>'
if 'Linux' in current_os:
    MYSQL_HOST = ''
    REDIS_HOST = '172.18.0.2:6379'
elif 'Darwin' in current_os:
    REDIS_HOST = '192.168.2.128:6379'
    MYSQL_HOST = '192.168.2.128'


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'aaaaaaaaaaaaaaaa'  # It must be 16, 24 or 32 bytes long

    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = 60*60*24
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=31)

    # Cache
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'cache:'
    CACHE_REDIS_URL = f'redis://{REDIS_HOST}'

    # Celery
    CELERY_BROKER_URL = f'redis://{REDIS_HOST}/3'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}/4'
    CELERY_TASK_RESULT_EXPIRES = 10

    # Mail
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_USERNAME = 'flask@outlook.com'
    MAIL_PASSWORD = 'flask'
    MAIL_PORT = 587  # 默认为25
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = (NAME, MAIL_USERNAME)  # 可迭代二元对象:(发送者姓名，发送者邮箱)，也可只有一外发送邮箱


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


class DevelopmentConfig(Config):  # 根据实际情况修改配置参数
    DEBUG = True
    db_info = {
        'ENGINE': 'mysql',
        'DRIVER': 'pymysql',
        'USER': '',
        'PASSWORD': '',
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
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': 3306,
        'NAME': 'blog'
    }
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


envs = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}


celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
