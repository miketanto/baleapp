from os import environ, path
from dotenv import load_dotenv
import secrets
import redis
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Base config."""
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url("redis://localhost:6379")
    TEMPLATES_AUTO_RELOAD = True
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SECRET_KEY = 'random'
    FLASK_ENV = 'development'
    FLASK_APP = 'wsgi.py'
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://root:Indrasari_12@127.0.0.1:3306/orderscheme'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    COMPRESSOR_DEBUG = False
