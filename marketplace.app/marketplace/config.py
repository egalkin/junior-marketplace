from dotenv import load_dotenv
import os

load_dotenv()


class Base(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/user_images'
   
    MAIL_SERVER = 'smtp.mail.ru'
    MAIL_PORT = 2525
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_DEFAULT_SENDER = 'xtramarket@rambler.ru'


    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL') or 'redis://localhost:6379/0',

    CACHE_STORAGE_HOST = 'localhost'
    CACHE_STORAGE_PORT = 6379
    CACHE_STORAGE_DB = 1
    REDIS_STORAGE_TIME = 1


class Development(Base):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost/marketplace.db'

    SECRET_KEY = 'secret-key'
    SECURITY_PASSWORD_SALT = 'secret-salt'

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
  

class Production(Base):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')

    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    
