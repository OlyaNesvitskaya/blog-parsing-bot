from io import StringIO, BytesIO
from pathlib import Path
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..models import Profile, Article, ParsingArticle


class ArticleModelTest(TestCase):

    def setUp(self):
        self.user = Profile.objects.create_user(username='user', password='password',
                                                email='user@gmail.com')
        self.article = Article.objects.create(
            title='Test title #1',
            content='Test title №1 is really important',
            profile=self.user
        )

    def test_title_label(self):
        article = Article.objects.get(id=self.article.id)
        field_label = article._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_content_label(self):
        article = Article.objects.get(id=self.article.id)
        field_label = article._meta.get_field('content').verbose_name
        self.assertEqual(field_label, 'content')

    def test_title_max_length(self):
        article = Article.objects.get(id=self.article.id)
        max_length = article._meta.get_field('title').max_length
        self.assertEqual(max_length, 120)

    def test_content_max_length(self):
        article = Article.objects.get(id=self.article.id)
        max_length = article._meta.get_field('content').max_length
        self.assertIsNone(max_length)

    def test_object_name_is_Article_of_title(self):
        article = Article.objects.get(id=self.article.id)
        expected_object_name = f'Article of {article.title}'
        self.assertEqual(str(article), expected_object_name)


class ParsingArticleModelTest(TestCase):

    def setUp(self):

        self.parsing_article = ParsingArticle.objects.create(
            headline='Test headline #1',
            url='http://test_headline#1.com',
        )

    def test_headline_label(self):
        parsing_article = ParsingArticle.objects.get(id=self.parsing_article.id)
        field_label = parsing_article._meta.get_field('headline').verbose_name
        self.assertEqual(field_label, 'headline')

    def test_url_label(self):
        parsing_article = ParsingArticle.objects.get(id=self.parsing_article.id)
        field_label = parsing_article._meta.get_field('url').verbose_name
        self.assertEqual(field_label, 'url')

    def test_headline_max_length(self):
        parsing_article = ParsingArticle.objects.get(id=self.parsing_article.id)
        max_length = parsing_article._meta.get_field('headline').max_length
        self.assertEqual(max_length, 1000)

    def test_url_max_length(self):
        parsing_article = ParsingArticle.objects.get(id=self.parsing_article.id)
        max_length = parsing_article._meta.get_field('url').max_length
        self.assertEqual(max_length, 1000)


class ProfileModelTest(TestCase):

    def setUp(self):
        self.test_image_path = (
                Path(__file__).resolve().parent.parent / "static/test_image.png"
        )

        im = Image.open(self.test_image_path)
        im_bytes = BytesIO()
        im.save(fp=im_bytes, format="PNG", quality=100)
        content = im_bytes.getvalue()
        newProfile = Profile(username='user', password='password',
                            email='user@gmail.com')
        newProfile.avatar = SimpleUploadedFile(
            name='default.png',
            content=content,
            content_type='image/jpeg')
        newProfile.save()

    def test_add_avatar(self):
        profile = Profile.objects.first()
        self.assertEqual(Profile.objects.count(), 1)
        profile.avatar.delete()
