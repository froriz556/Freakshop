from tkinter.constants import ACTIVE

from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm
from django.utils.html import strip_tags

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=66,
                             widget=forms.EmailInput(attrs={'placeholder': 'Ваш e-mail'}))
    first_name = forms.CharField(required=True, max_length=50,
                                 widget=forms.CharField(attrs={'placeholder': 'Имя'}))
    last_name = forms.CharField(required=True, max_length=50,
                                 widget=forms.CharField(attrs={'placeholder': 'Фамилия'}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Электронная почта уже занята!')
        else:
            return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None
        if commit:
            user.save()
        return user

class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(label='email', widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Адрес электронной почты'}))
    password = forms.CharField(label='password', widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Пароль'}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request(email=email, password=password))
            if self.user_cache is None:
                raise forms.ValidationError('Неправильная почта или пароль')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Этот аккаунт недействителен')
            return self.cleaned_data

class CustomUserUpdateForm(ModelForm):
    phone = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Введите корректный телефонный номер.')]
    )
    email = forms.EmailField(required=False, max_length=66,
                             widget=forms.EmailInput(attrs={'placeholder': 'Ваш e-mail'}))
    first_name = forms.CharField(required=True, max_length=50,
                                 widget=forms.CharField(attrs={'placeholder': 'Имя'}))
    last_name = forms.CharField(required=True, max_length=50,
                                 widget=forms.CharField(attrs={'placeholder': 'Фамилия'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            # 'phone': forms.TextInput(attrs={'class': 'input'})
        }

    def clean_email(self):
        email =self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Адрес электронной почты уже занят')
        return email

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email

            for field in ['phone']:
                if cleaned_data.get(field):
                    cleaned_data[field] = strip_tags(cleaned_data[field])

                return  cleaned_data