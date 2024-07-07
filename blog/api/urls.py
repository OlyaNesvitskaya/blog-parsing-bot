from django.urls import path

from .views import (
    ApiArticle,
    ApiArticleDetail,
    ApiLatestArticleDetail,
    ApiLatestParsingArticle,
    login_view,
    logout_view
)

urlpatterns = [
    path('login/', login_view, name='api_login'),
    path('logout/', logout_view, name='api_logout'),
    path('articles/', ApiArticle.as_view(), name='articles'),
    path('article/<pk>/', ApiArticleDetail.as_view(), name='article'),
    path('latest_web_article/', ApiLatestArticleDetail.as_view(), name='latest_web_article'),
    path('latest_parsing_article/', ApiLatestParsingArticle.as_view(), name='latest_parsing_article'),
]