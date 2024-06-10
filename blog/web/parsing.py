import requests
from bs4 import BeautifulSoup

from .models import ParsingArticle

URL = 'https://news.ycombinator.com/'


def get_html(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text


def get_data(html: str) -> None:
    soup = BeautifulSoup(html, 'lxml')
    articles = soup.find_all('span', {'class': 'titleline'})
    for article in articles:
        article_from_site = article.find('span', {'class': 'sitebit comhead'})
        if article_from_site:
            tag_a = article.find('a')
            url = tag_a.get('href')
            headline = tag_a.text
            ParsingArticle.objects.get_or_create(url=url, defaults={'headline': headline})


def main():

    html = get_html(URL)
    get_data(html)


if __name__ == '__main__':
    main()

