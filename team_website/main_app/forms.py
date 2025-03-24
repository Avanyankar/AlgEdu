from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrationForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей.
    Наследуется от UserCreationForm и добавляет email-поле с валидацией.
    """
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    password1 = forms.CharField(
        label=_('Пароль'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Пароль должен содержать минимум 8 символов.'),
    )
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_('Введите тот же пароль, что и выше, для проверки.'),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': _('Логин'),
            'password1': _('Пароль'),
            'password2': _('Подтверждение пароля'),
        }
        help_texts = {
            'username': _('Только буквы, цифры и @/./+/-/_'),
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Логин')
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Пользователь с таким email уже существует.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Пользователь с таким именем уже существует.'))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
