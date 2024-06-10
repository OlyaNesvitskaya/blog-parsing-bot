from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..forms import *
from ..models import Profile


class TestProfileForm(TestCase):
    def setUp(self):
        self.test_image_path = (
                Path(__file__).resolve().parent.parent / "static/test_image.png"
        )

    def test_filled_form(self):
        avatar = SimpleUploadedFile(name='test_image.jpg', content=open(self.test_image_path, 'rb').read(),
                                    content_type='image/jpeg')
        data = {'avatar': avatar,
                'email': 'qw@gmail.com',
                'username': 'qwerty',
                'password': 'qwerty',
                'password2': 'qwerty'}

        form = UserRegistrationForm(data=data)
        self.assertIn("avatar", form.fields)
        self.assertTrue(form.is_valid())

    def test_edit_user_form(self):
        data = {'email': 'qw@gmail.com',
                'username': 'qwerty',
                'password': 'qwerty',
                'password2': 'qwerty'}

        form = EditUserForm(data=data)
        self.assertIn("avatar", form.fields)
        self.assertTrue(form.is_valid())


def test_user_registration_form_with_different_passwords(self):
    with open(self.test_image_path, "rb") as image_file:
        data = {'avatar': image_file,
                'email': 'qw@gmail.com',
                'username': 'qwerty',
                'password': 'qwerty',
                'password2': 'qw'}
    form = UserRegistrationForm(data=data)
    self.assertFalse(form.is_valid())
    self.assertEqual(
        form.errors["password2"], ["Passwords don\'t match."]
    )


class TestArticleForm(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(username='Karenina', email='ankar@gmail.com', avatar='')

    def test_article_form_valid(self):
        data = {'title': 'Test title', 'content': 'Test titleTest titleTest title', 'profile': self.profile}
        form = ArticleForm(data=data)
        self.assertTrue(form.is_valid())

