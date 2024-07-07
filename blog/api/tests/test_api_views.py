from parameterized import parameterized
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse

from web.models import Article, Profile, ParsingArticle
from ..serializers import *


class ArticleApiTest(APITestCase):
    def setUp(self):
        self.profile = Profile.objects.create_user(email='ankar@gmail.com', username='testuser',
                                                   password='1234', avatar='')

        login_data = {
            'username': 'testuser',
            'password': '1234',
        }
        login_response = self.client.post(reverse('api_login'), login_data, format='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.new_article = {'title': 'Test title', 'content': 'Test titleTest titleTest title', 'profile': self.profile}
        self.article = Article.objects.create(**self.new_article)
        self.token, created = Token.objects.get_or_create(user=self.profile)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def get_profile_token(self, email: str, username: str, password: str):
        profile = Profile.objects.create(avatar='', email=email, username=username,
                                          password=password)
        login_data = {
            'username': profile.username,
            'password': profile.password,
        }
        self.client.post('/api/login/', login_data, format='json')
        token, created = Token.objects.get_or_create(user=profile)
        return token

    def test_get_single_article(self):
        response = self.client.get(reverse('article', kwargs={'pk': self.article.id}), format='json')
        data = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], self.new_article['title'])
        self.assertTrue(data['url'], 'http://127.0.0.1:8000/web/article_detail/1')

    def test_get_single_article_by_another_user(self):
        self.client.logout()
        token = self.get_profile_token(email='testuser2@gmail.com', username='testuser2',
                                          password='1234')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(f'/api/article/{self.article.id}/', format='json')
        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], self.new_article['title'])
        self.assertTrue(data['url'], 'http://127.0.0.1:8000/web/article_detail/1')

    def test_update_valid_single_article(self):
        data = {'title': 'Update Test title', 'content': 'Update Test titleTest titleTest title'}
        response = self.client.patch(reverse('article', kwargs={'pk': self.article.id}), data=data, format='json')

        updated_article = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_article['title'], data['title'])
        self.assertTrue(updated_article['url'], 'http://127.0.0.1:8000/web/article_detail/1')

    def test_update_single_article_by_another_user(self):
        self.client.logout()
        token = self.get_profile_token(email='testuser2@gmail.com', username='testuser2',
                                       password='1234')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        data = {'title': 'Update2 Test title', 'content': 'Update2 Test titleTest titleTest title'}
        response = self.client.patch(reverse('article', kwargs={'pk': self.article.id}), data=data, format='json')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('detail'), 'You do not have permission to perform this action.')

    def test_update_invalid_single_article(self):
        data = {'title': 'Update Test title', 'content': 'Update Test titleTest titleTest title'}
        response = self.client.patch(reverse('article', kwargs={'pk': 100}), data=data, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get('detail'), 'No Article matches the given query.')

    def test_delete_invalid_single_article(self):
        response = self.client.delete(reverse('article', kwargs={'pk': 100}), format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get('detail'), 'No Article matches the given query.')

    def test_delete_single_article_by_another_user(self):
        self.client.logout()
        token = self.get_profile_token(email='testuser2@gmail.com', username='testuser2',
                                       password='1234')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.delete(reverse('article', kwargs={'pk': self.article.id}), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('detail'), 'You do not have permission to perform this action.')

    def test_delete_single_article(self):
        response = self.client.delete(reverse('article', kwargs={'pk': self.article.id}), format='json')
        self.assertEqual(response.status_code, 204)

    def test_get_latest_web_article(self):
        response = self.client.get(reverse('latest_web_article'), format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], self.new_article['title'])
        self.assertTrue(data['url'], 'http://127.0.0.1:8000/web/article_detail/1')

    def test_get_latest_parsing_article_with_empty_table(self):
        response = self.client.get(reverse('latest_parsing_article'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual({}, {})

    def test_get_latest_parsing_article(self):
        self.parsing_article = {'headline': 'Medium article', 'url': 'https://medium_article.com'}
        self.parsing_article_obj = ParsingArticle.objects.create(**self.parsing_article)
        response = self.client.get(reverse('latest_parsing_article'), format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], self.parsing_article['headline'])
        self.assertTrue(data['url'], self.parsing_article['url'])

    def test_post_article_with_data(self):
        data = {'title': 'Test title5', 'content': 'Test title5Test title5Test title', 'profile': self.profile.id}
        response = self.client.post(reverse('articles'), data=data, format='json')
        new_article = response.json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(new_article['title'], data['title'])
        self.assertEqual(new_article['profile'], data['profile'])

    def test_post_article_without_data(self):
        response = self.client.post(reverse('articles'), data={}, format='json')
        self.assertEqual(response.status_code, 400)


class GetAllArticlesApiTest(APITestCase):
    def setUp(self):
        self.profile = Profile.objects.create(avatar='', email='ankar@gmail.com', username='testuser', password='1234')

        login_data = {
            'username': 'testuser',
            'password': '1234',
        }

        self.client.post(reverse('api_login'), login_data, format='json')
        self.token, created = Token.objects.get_or_create(user=self.profile)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.article1 = Article.objects.create(id=1, title='Test title1', content='Test title1', profile=self.profile)
        self.article2 = Article.objects.create(id=2, title='Test title2', content='Test title2', profile=self.profile)
        self.article3 = Article.objects.create(id=3, title='Test title3', content='Test title3', profile=self.profile)
        self.article4 = Article.objects.create(id=4, title='Test title4', content='Test title4', profile=self.profile)

        self.parsing_article1 = ParsingArticle.objects.create(id=1, headline='Medium article1',
                                                              url='https://medium_article1.com')
        self.parsing_article2 = ParsingArticle.objects.create(id=2, headline='Medium article2',
                                                              url='https://medium_article2.com')
        self.parsing_article3 = ParsingArticle.objects.create(id=3, headline='Medium article3',
                                                              url='https://medium_article3.com')
        self.parsing_article4 = ParsingArticle.objects.create(id=4, headline='Medium article4',
                                                              url='https://medium_article4.com')

    def test_get_articles_without_parameters(self):

        response = self.client.get(reverse('articles'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(response.data, serializer.data)

    @parameterized.expand([
        ('parsing=0&id_from=1&id_to=2', [
            {'id': 2, 'title': 'Test title2', 'url': 'http://127.0.0.1:8000/web/article_detail/2'},
            {'id': 1, 'title': 'Test title1', 'url': 'http://127.0.0.1:8000/web/article_detail/1'}
        ]),

        ('id_from=4', [
            {'id': 4, 'title': 'Test title4', 'url': 'http://127.0.0.1:8000/web/article_detail/4'}
        ]),

        ('id_to=3', [
            {'id': 3, 'title': 'Test title3', 'url': 'http://127.0.0.1:8000/web/article_detail/3'},
            {'id': 2, 'title': 'Test title2', 'url': 'http://127.0.0.1:8000/web/article_detail/2'},
            {'id': 1, 'title': 'Test title1', 'url': 'http://127.0.0.1:8000/web/article_detail/1'}
        ]),
    ])
    def test_get_web_articles_with_parameters(self, query_params, result):

        response = self.client.get(f'/api/articles/?{query_params}', format='json')
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for index, article in enumerate(data):
            self.assertEqual(article['id'], result[index]['id'])
            self.assertEqual(article['title'], result[index]['title'])
            self.assertEqual(article['url'], result[index]['url'])

    @parameterized.expand([
        ('parsing=1&id_from=1&id_to=2', [
            {'id': 1, 'title': 'Medium article1', 'url': 'https://medium_article1.com'},
            {'id': 2, 'title': 'Medium article2', 'url': 'https://medium_article2.com'}
        ]),

        ('parsing=1&id_from=4', [
            {'id': 4, 'title': 'Medium article4', 'url': 'https://medium_article4.com'}
        ]),

        ('parsing=1&id_to=3', [
            {'id': 1, 'title': 'Medium article1', 'url': 'https://medium_article1.com'},
            {'id': 2, 'title': 'Medium article2', 'url': 'https://medium_article2.com'},
            {'id': 3, 'title': 'Medium article3', 'url': 'https://medium_article3.com'}
        ])
    ])
    def test_get_parsing_articles_with_parameters(self, query_params, result):
        response = self.client.get(f'/api/articles/?{query_params}', format='json')
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for index, article in enumerate(data):
            self.assertEqual(article['id'], result[index]['id'])
            self.assertEqual(article['title'], result[index]['title'])
            self.assertEqual(article['url'], result[index]['url'])
