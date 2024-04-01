from django import forms
from django.contrib.auth.forms import UserCreationForm

from administration.models import User
from administration.models.article import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'url', 'summary']


class UserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'type': 'username', 'placeholder': ('Username')}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'first_name', 'placeholder': ('First Name')}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'last_name', 'placeholder': ('Last Name')}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email', 'placeholder': ('Email')}))
    password1 = forms.CharField(
        max_length=16,
        widget=forms.PasswordInput(
            attrs={
                # 'class':'form-control',
                'placeholder': 'Password'
            }
        ),
    )
    password2 = forms.CharField(
        max_length=16,
        widget=forms.PasswordInput(
            attrs={
                # 'class':'form-control',
                'placeholder': 'Repeat Password'
            }
        ),
    )
    group_choices = (
        ('M', 'Manager'),
        ('U', 'User'),
        ('C', 'Customer'),
    )
    groups = forms.ChoiceField(choices=group_choices)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'groups']
