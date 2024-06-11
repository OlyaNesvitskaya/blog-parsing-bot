from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='uploads/', default='uploads/default.png')

    def __str__(self):
        return f'Profile of {self.username}'


class Article(models.Model):
    title = models.CharField(max_length=120, unique=True)
    content = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-publication_date']

    def __str__(self):
        return f'Article of {self.title}'


class ParsingArticle(models.Model):
    headline = models.CharField(max_length=1000)
    url = models.URLField(max_length=1000, unique=True)
    added_date = models.DateTimeField(auto_now_add=True)

