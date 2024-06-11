import time
import schedule
import requests

from main import (
    get_latest_article, url_latest_web_article, bot, url_latest_site_article,
    logger)
from work_with_db import get_article_ids, update_article_ids, get_all_users
from settings import host, get_token


def get_new_articles(url: str, last_article_id_db: int, parsing: int = 0) -> list:
    latest_article = get_latest_article(url)

    if latest_article:
        last_article_id = latest_article.get('id')
        new_articles = last_article_id - last_article_id_db
        if new_articles > 0:
            headers = {"Content-Type": "application/json; charset=utf-8",
                       "Authorization": get_token()}
            response = requests.get(
                f'http://{host}:8000/api/articles/'
                f'?parsing={parsing}'
                f'&id_from={last_article_id_db + 1}'
                f'&id_to={last_article_id}',
                headers=headers
            )
            if response.status_code == 200:
                return response.json()


def send_new_articles_to_user() -> None:
    new_articles = get_new_articles(url_latest_web_article, get_article_ids('article'))
    parsing_articles = get_new_articles(url_latest_site_article, get_article_ids('parsingarticle'), parsing=1)

    send_articles = []
    if new_articles:
        send_articles.extend(new_articles)
        update_article_ids('article', new_articles[0]['id'])
    if parsing_articles:
        send_articles.extend(parsing_articles)
        update_article_ids('parsingarticle', parsing_articles[-1]['id'])

    for telegram_id in get_all_users():
        for article in send_articles:
            bot.send_message(
                telegram_id,
                text=f'[{article.get( "title" )}]({article.get( "url" )})',
                parse_mode='Markdown'
            )


def schedule_actions():
    schedule.every(5).minutes.do(send_new_articles_to_user)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":

    while True:
        try:
            schedule_actions()
        except Exception as e:
            time.sleep(5)
            logger.error(e)
        continue