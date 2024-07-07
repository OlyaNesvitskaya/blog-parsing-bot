from django import forms
from django.utils.safestring import SafeString

from .models import Profile, Article


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    error_css_class = "error"

    class Meta:
        model = Profile
        fields = ('username', 'email', 'avatar')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label

    def as_div(self):
        return SafeString(super().as_div().replace("<div>", "<div class='mb-3 row'>"))


class EditUserForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('username', 'email', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label

    def as_div(self):
        return SafeString(super().as_div().replace("<div>", "<div class='mb-3 row'>"))


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content')
        widgets = {'profile': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label

    def as_div(self):
        return SafeString(super().as_div().replace("<div>", "<div class='mb-3 row'>"))
