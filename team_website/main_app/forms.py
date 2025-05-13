from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from main_app.models import User, Comment, Field, FieldReport


class RegistrationForm(UserCreationForm):
    """
    A form for registering new users.
    Inherits from the UserCreationForm and adds an email field with validation.
    """
    email = forms.EmailField(
        label=gettext_lazy('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    password1 = forms.CharField(
        label=gettext_lazy('Пароль'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=gettext_lazy('Пароль должен содержать минимум 8 символов.'),
    )
    password2 = forms.CharField(
        label=gettext_lazy('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=gettext_lazy('Введите тот же пароль, что и выше, для проверки.'),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': gettext_lazy('Логин'),
            'password1': gettext_lazy('Пароль'),
            'password2': gettext_lazy('Подтверждение пароля'),
        }
        help_texts = {
            'username': gettext_lazy('Только буквы, цифры и @/./+/-/_'),
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': gettext_lazy('Логин')
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(gettext_lazy('Пользователь с таким email уже существует.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(gettext_lazy('Пользователь с таким именем уже существует.'))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'location', 'birth_date', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }
        labels = {
            'first_name': gettext_lazy('Имя'),
            'last_name': gettext_lazy('Фамилия'),
            'email': gettext_lazy('Email'),
            'location': gettext_lazy('Местоположение'),
            'birth_date': gettext_lazy('Дата рождения'),
            'bio': gettext_lazy('О себе'),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(gettext_lazy('Этот email уже используется'))
        return email

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date.year < 1900:
            raise ValidationError(gettext_lazy('Некорректная дата рождения'))
        return birth_date

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'comment-input',
                'placeholder': 'Write your comment...'
            }),
        }

class DBFileField(forms.FileField):
    def to_python(self, data):
        data = super().to_python(data)
        if data is None:
            return None

        return {
            'name': data.name,
            'content_type': data.content_type,
            'size': data.size,
            'data': data.read()
        }


class FieldForm(forms.ModelForm):
    file = DBFileField(required=False, label="Прикрепленный файл")

    class Meta:
        model = Field
        fields = ['title', 'description', 'cols', 'rows']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'cols': forms.NumberInput(attrs={'min': 1, 'max': 20}),
            'rows': forms.NumberInput(attrs={'min': 1, 'max': 20}),
        }
        labels = {
            'cols': 'Количество колонок',
            'rows': 'Количество строк',
        }

class FieldReportForm(forms.ModelForm):
    class Meta:
        model = FieldReport
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
