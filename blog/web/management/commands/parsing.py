import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand

from web.parsinglog import logger
from web.models import ParsingArticle

URL = 'https://news.ycombinator.com/'


def get_html(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text

    logger.error(f'{url} returned the code {response.status_code}')


def get_data(html: str) -> None:
    soup = BeautifulSoup(html, 'lxml')
    articles = soup.find_all('span', {'class': 'titleline'})
    if not articles:
        logger.warning('The array of articles is empty.'
                       'The span tag is missing a {"class": "titleline"}')
        return

    for article in articles:
        article_from_site = article.find('span', {'class': 'sitebit comhead'})
        if article_from_site is None:
            logger.warning('The article cannot be found.'
                           'The span tag is missing a {"class": "sitebit comhead"}')
            continue

        tag_a = article.find('a')

        url = tag_a.get('href')
        if url is None or len(url) > 1000:
            logger.info('The link is empty or the length exceeds the allowed value.')
            continue

        headline = tag_a.text
        if headline is None or len(headline) > 1000:
            logger.info('The headline is empty or the length exceeds the allowed value')
            continue

        try:
            parsing_article, created = ParsingArticle.objects.get_or_create(
                url=url,
                defaults={'headline': headline}
            )
            if created:
                logger.info(f'Added new article {url}')

        except Exception:
            logger.exception('Article adding error to database')


def main():
    logger.info('RUN SITE PARSING')
    html = get_html(URL)

    if html is not None:
        get_data(html)


class Command(BaseCommand):
    help = 'Parsing articles "https://news.ycombinator.com/"'

    def handle(self, *args, **options):
        main()
        self.stdout.write(self.style.SUCCESS('Parsing articles'))

