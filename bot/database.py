import sqlite3
from sqlite3 import Error
from botlog import logger
from settings import db_name


def create_connection(db_name: str):
    connection = None
    try:
        connection = sqlite3.connect(db_name, check_same_thread=False)
    except Error as e:
        logger.exception(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query, params=tuple()):
    cursor = connection.cursor()
    try:
        a = cursor.execute(query, params)
        connection.commit()
        return a
    except Error as e:
        logger.error(f"The error '{e}' occurred")


connection = create_connection(db_name)


create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  telegram_id INTEGER NOT NULL
);
"""


create_articles_id_table = """
CREATE TABLE IF NOT EXISTS article_ids (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL UNIQUE,
  last_article_id INTEGER NOT NULL
);
"""


def create_databases():
    execute_query(connection, create_users_table)
    execute_query(connection, create_articles_id_table)





