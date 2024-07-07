from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('', views.ArticleListView.as_view(), name='home'),
    path('<user_articles>', views.UserArticleListView.as_view(), name='user_articles'),

    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="web/logout.html"), name='logout'),
    path('register/', views.register, name='register'),
    path('edit_profile/', views.update_profile, name='update_profile'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="web/password_reset_form.html"), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="web/password_reset_done.html"), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="web/password_reset_confirm.html"), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="web/password_reset_complete.html"), name='password_reset_complete'),

    path('article_add/', views.ArticleCreateView.as_view(), name='article_add'),
    path("article_detail/<int:pk>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path('article_edit/<pk>', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('article_delete/<pk>', views.ArticleDeleteView.as_view(), name='article_delete')
]
