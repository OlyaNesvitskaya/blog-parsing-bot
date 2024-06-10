import operator
from functools import reduce

from database import execute_query, connection


def create_user(telegram_id: int) -> None:
    execute_query(
        connection,
        'INSERT INTO users (telegram_id) VALUES (?);',
        (telegram_id,))


def get_all_users() -> tuple:
    """Get tuple of telegram_id"""
    data = execute_query(
        connection,
        'SELECT telegram_id FROM users;'
        ).fetchall()
    return reduce(operator.add, data, tuple())


def is_user_exist(telegram_id: int):
    """Check if user exist"""
    data = execute_query(
        connection,
        'SELECT * FROM users WHERE telegram_id=?;',
        (telegram_id,)
    )
    return data.fetchone()


def create_article_ids(source: str, last_article_id: int) -> None:
    data = execute_query(connection, 'INSERT INTO article_ids (source, last_article_id) VALUES (?, ?);',
                         (source, last_article_id))


def get_article_ids(source: str) -> int | None:
    data = execute_query(
        connection,
        'SELECT last_article_id FROM article_ids WHERE source=?;',
        (source,)
    ).fetchone()
    if data:
        return data[0]


def update_article_ids(source: str, last_article_id: int) -> None:
    execute_query(
        connection,
        "UPDATE article_ids SET last_article_id = ? WHERE source = ?",
        (last_article_id, source)
    )
