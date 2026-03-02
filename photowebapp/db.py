import os

import pymysql
from pymysql.cursors import DictCursor

from .config import get_required_env


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=get_required_env("DB_USER"),
        password=get_required_env("DB_PASSWORD"),
        database=get_required_env("DB_NAME"),
        cursorclass=DictCursor,
        autocommit=True,
    )
