import os

import requests
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()
bot = TeleBot(os.environ.get("TELEGRAM_TOKEN"))
host = os.environ.get("HOST")
url_latest_web_article = f'http://{host}:8000/api/latest_web_article/'
url_latest_site_article = f'http://{host}:8000/api/latest_parsing_article/'
url_get_token = f'http://{host}:8000/api/login/'
db_name = os.environ.get("DB_NAME")


def get_token() -> str:
    login_data = {
        'username': 'botuser',
        'password': 'botuser',
    }
    response = requests.post(url_get_token, json=login_data)
    if response.status_code == 200:
        return f'Token {response.json().get("token")}'