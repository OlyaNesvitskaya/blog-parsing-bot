import time
from telebot.types import BotCommand, Message
import requests
import prettytable as pt

from botlog import logger
from work_with_db import create_user, is_user_exist
from database import create_databases
from work_with_db import update_article_ids, get_article_ids, create_article_ids
from settings import bot, url_latest_site_article, url_latest_web_article, get_token

start_command = BotCommand(command='start', description='start')
help_command = BotCommand(command='help', description='get_list_of_available_commands')
latest_command = BotCommand(command='latest', description='get latest article')

bot.set_my_commands([start_command, help_command, latest_command])


@bot.message_handler(commands=['start'])
def send_hello(message: Message) -> None:
    chat_id = message.chat.id
    if not is_user_exist(chat_id):
        create_user(chat_id)

    bot.send_message(
        message.chat.id,
        text='Hello.\n I\'m a bot that will send you new interesting articles',
    )


def get_latest_article(url: str) -> dict:
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": get_token()}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()


@bot.message_handler(commands=['help'])
def get_list_of_available_commands(message: Message) -> None:
    table = pt.PrettyTable(['№', 'command', 'description'])
    table.border = False
    table.header_style = 'upper'
    table.align = 'l'

    for index, command in enumerate(bot.get_my_commands(), start=1):
        table.add_row([index, command.command,  command.description])

    bot.send_message(
        message.chat.id,
        text=table.get_string()
    )


@bot.message_handler(commands=['latest'])
def send_latest_article_to_user(message: Message) -> None:
    article = get_latest_article(url_latest_web_article)
    if article:
        bot.send_message(
            message.chat.id,
            text=f'[{article.get("title")}]({article.get("url")})',
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            message.chat.id,
            text=f'Articles hasn\'t had yet ((('
        )


def update_or_set_initial_data(
        source: str,
        url_latest_web_article: str,
        initial_article_id: int = 0
):
    article = get_latest_article(url_latest_web_article)
    article_in_db = get_article_ids(source)
    if article == {} and article_in_db is None:
        create_article_ids(source, initial_article_id)
    elif article and article_in_db is None:
        create_article_ids(source, article.get('id'))
    elif article and article_in_db and article.get('id') != article_in_db:
        update_article_ids(source, article.get('id'))
    elif article == {} and article_in_db:
        update_article_ids(source, 0)


if __name__ == "__main__":
    time.sleep(60)
    create_databases()
    logger.info('Start BOT')
    update_or_set_initial_data('article', url_latest_web_article)
    update_or_set_initial_data('parsingarticle', url_latest_site_article)

    bot.polling(none_stop=True, interval=1, timeout=30)
