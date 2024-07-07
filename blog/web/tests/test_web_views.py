from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from ..forms import *
from ..models import Profile


class GetAllArticlesWebTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Profile.objects.create_user(username='user', password='password',
                                                email='user@gmail.com')
        for article_num in range(1, 7):
            Article.objects.create(
                title=f'title №{article_num}',
                content=f'Test title №{article_num}',
                profile=self.user
            )

        self.client.login(username='user', password='password')

    def test_article_list_view_with_login(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/all_articles.html')

    def test_article_list_view_without_login(self):
        self.client.logout()
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/home.html')


class ArticleWebTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Profile.objects.create_user(username='user', password='password',
                                                email='user@gmail.com')
        self.article = Article.objects.create(
            title=f'first article',
            content=f'first article is very interesting!',
            profile=self.user
        )

        self.client.login(username='user', password='password')

    def test_published_article(self):
        self.client.post(reverse('article_add'), {'title': "Super Important Article",
                                               'content': "This is really important.", 'profile_id': self.user.id})
        created_article = Article.objects.first()

        self.assertEqual(created_article.title, "Super Important Article")
        self.assertEqual(created_article.content, "This is really important.")

    def test_display_article(self):
        article = Article.objects.create(
            title=f'title №100',
            content=f'Test title №100 really important',
            profile=self.user
        )
        response = self.client.get(reverse('article_detail', args=(article.pk,)))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/article_detail.html')

    def test_article_detail_view(self):
        response = self.client.get(reverse('article_detail', args=(self.article.pk,)))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/article_detail.html')

    def test_get_article_update_page(self):
        response = self.client.get(reverse('article_edit', args=(self.article.pk,)))

        self.article.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/article_edit.html')

    def test_update_article(self):
        response = self.client.post(
            reverse('article_edit', kwargs={'pk': self.article.id}),
            {'title': 'Update first article title', 'content': 'Update first article content'})

        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Update first article title')

    def test_get_article_delete_page(self):
        response = self.client.get(reverse(
            'article_delete', args=(self.article.id,)),
            follow=True
        )
        self.assertContains(response, f'Are you sure you want to delete')  # THIS PART WORKS

    def test_delete_article(self):
        post_response = self.client.post(reverse('article_delete', args=(self.article.id,)), follow=True)
        self.assertRedirects(post_response, reverse('home'), status_code=302)


class ProfileWebTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Profile.objects.create_user(username='user', password='password',
                                                email='user@gmail.com')
        self.test_image_path = (
                Path(__file__).resolve().parent.parent / "static/test_image.png"
        )

        self.client.login(username='user', password='password')

    def test_get_profile_update_page(self):
        response = self.client.get(reverse('update_profile'))
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/edit_profile.html')

    def test_update_profile(self):
        response = self.client.post(
            reverse('update_profile'),
            {'username': 'update_user', 'email': 'updateuser@gmail.com'})

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'update_user')

    def test_register_profile(self):
        self.client.logout()
        avatar = SimpleUploadedFile(name='test_image.jpg', content=open(self.test_image_path, 'rb').read(),
                                    content_type='image/jpeg')
        data = {
            'username': 'Olga',
            'email': 'nesvitulka@gmail.com',
            'password': 1234,
            'password2': 1234,
            'avatar': avatar
        }

        self.client.post(reverse('register'), data=data)
        created_profile = Profile.objects.last()

        self.assertEqual(created_profile.username, 'Olga')
        self.assertEqual(created_profile.email, 'nesvitulka@gmail.com')
