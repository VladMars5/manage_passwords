import os
import string
import logging

from dotenv import load_dotenv

load_dotenv(os.environ.get("ENV_FILE") if os.environ.get("ENV_FILE") else None)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

SECRET_AUTH = os.environ.get("SECRET_AUTH")

LIVE_POOL_DB_CONNECTIONS = int(os.environ.get("LIVE_POOL_DB_CONNECTIONS"))
COUNT_MAX_CONNECTIONS_DB = int(os.environ.get("COUNT_MAX_CONNECTIONS_DB"))
COUNT_OVERFLOW_POOL = int(os.environ.get("COUNT_OVERFLOW_POOL"))

JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY')
JWT_ALGORITHM: str = os.environ.get('JWT_ALGORITHM')
JWT_EXPIRE_MINUTES: int = int(os.environ.get('JWT_EXPIRE_MINUTES'))
JWT_EXPIRE_MINUTES_RESET_PASSWORD: int = int(os.environ.get('JWT_EXPIRE_MINUTES_RESET_PASSWORD'))

SMTP_HOST: str = os.environ.get('SMTP_HOST')
SMTP_PORT: int = int(os.environ.get('SMTP_PORT'))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

REDIS_HOST: str = os.environ.get('REDIS_HOST')
REDIS_PORT: int = int(os.environ.get('REDIS_PORT'))
REDIS_DB: str = os.environ.get('REDIS_DB')

ENCRYPTION_KEY: bytes = os.environ.get('ENCRYPTION_KEY').encode('utf-8')

subjects = {'reset_password': 'Сброс пароля PasswordManager для пользователя {} сервиса ManagePassword'}
alphabet_password = string.ascii_letters + string.digits + string.punctuation

LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False
WORKERS = int(os.environ.get("GUNICORN_WORKERS", "5"))
