from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView

from .forms import UserRegistrationForm, EditUserForm, ArticleForm
from .models import Article


class MyLoginView(LoginView):
    template_name = "web/login.html"

    def get_success_url(self):
        next_page = self.request.POST.get('next')
        if '/web/article/' in next_page:
            return reverse('article_detail', kwargs={"pk": next_page.split('/')[-2]})
        else:
            return super().get_success_url()


@transaction.atomic
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password'])
            new_user.save()
            return render(request,
                          'web/register_done.html',
                          {'new_user': new_user, 'next': request.GET.get("next", '/web/')})

    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'web/register.html',
                  {'user_form': user_form})


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('home')
    else:
        user_form = EditUserForm(instance=request.user)
    return render(request,
                  'web/edit_profile.html',
                  {'user_form': user_form})


class ArticleListView(ListView):
    model = Article
    template_name = 'web/all_articles.html'


class UserArticleListView(ListView):
    model = Article
    template_name = 'web/user_articles.html'

    def get_queryset(self):
        return Article.objects.filter(profile=self.request.user)


class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'web/article_add.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.profile = self.request.user
        return super().form_valid(form)


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'web/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'web/article_edit.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.profile = self.request.user
        return super().form_valid(form)


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'web/article_delete.html'
    success_url = reverse_lazy('home')