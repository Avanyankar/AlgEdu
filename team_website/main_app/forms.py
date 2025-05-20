"""
Формы Django для обработки пользовательских данных.

Этот модуль определяет формы для регистрации пользователей, обновления профиля,
создания комментариев, полей и жалоб на поля.

:mod:`main_app.forms`
"""

from typing import Optional, Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy
from main_app.models import User, Comment, Field, FieldReport


class RegistrationForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей.

    Наследуется от :class:`django.contrib.auth.forms.UserCreationForm` и добавляет
    поле email с валидацией.

    :attribute email: Поле для ввода email.
    :type email: :class:`django.forms.EmailField`
    :attribute password1: Поле для ввода пароля.
    :type password1: :class:`django.forms.CharField`
    :attribute password2: Поле для подтверждения пароля.
    :type password2: :class:`django.forms.CharField`
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
        help_text=gettext_lazy('Пароль должен содержать минимум 8 символов.')
    )
    password2 = forms.CharField(
        label=gettext_lazy('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=gettext_lazy('Введите тот же пароль, что и выше, для проверки.')
    )

    class Meta:
        """
        Мета-данные для формы.

        :attribute model: Модель, связанная с формой.
        :type model: :class:`main_app.models.User`
        :attribute fields: Поля формы.
        :type fields: tuple[str, ...]
        :attribute labels: Метки для полей.
        :type labels: dict[str, str]
        :attribute help_texts: Подсказки для полей.
        :type help_texts: dict[str, str]
        :attribute widgets: Виджеты для полей.
        :type widgets: dict[str, :class:`django.forms.Widget`]
        """
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

    def clean_email(self) -> str:
        """
        Проверяет уникальность email.

        :returns: Проверенный email.
        :rtype: str
        :raises ValidationError: Если email уже используется.
        """
        email: str = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(gettext_lazy('Пользователь с таким email уже существует.'))
        return email

    def clean_username(self) -> str:
        """
        Проверяет уникальность имени пользователя.

        :returns: Проверенное имя пользователя.
        :rtype: str
        :raises ValidationError: Если имя пользователя уже используется.
        """
        username: str = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(gettext_lazy('Пользователь с таким именем уже существует.'))
        return username

    def save(self, commit: bool = True) -> User:
        """
        Сохраняет пользователя с указанным email.

        :param commit: Сохранять ли объект в базе данных.
        :type commit: bool
        :returns: Созданный пользователь.
        :rtype: :class:`main_app.models.User`
        """
        user: User = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """
    Форма для обновления профиля пользователя.

    :attribute Meta.model: Модель, связанная с формой.
    :type Meta.model: :class:`main_app.models.User`
    """
    class Meta:
        """
        Мета-данные для формы.

        :attribute model: Модель, связанная с формой.
        :type model: :class:`main_app.models.User`
        :attribute fields: Поля формы.
        :type fields: list[str]
        :attribute widgets: Виджеты для полей.
        :type widgets: dict[str, :class:`django.forms.Widget`]
        :attribute labels: Метки для полей.
        :type labels: dict[str, str]
        """
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

    def clean_email(self) -> str:
        """
        Проверяет уникальность email, исключая текущего пользователя.

        :returns: Проверенный email.
        :rtype: str
        :raises ValidationError: Если email уже используется другим пользователем.
        """
        email: str = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(gettext_lazy('Этот email уже используется'))
        return email

    def clean_birth_date(self) -> Optional[Any]:
        """
        Проверяет корректность даты рождения.

        :returns: Проверенная дата рождения.
        :rtype: Optional[:class:`datetime.date`]
        :raises ValidationError: Если год рождения меньше 1900.
        """
        birth_date: Optional[Any] = self.cleaned_data.get('birth_date')
        if birth_date and birth_date.year < 1900:
            raise ValidationError(gettext_lazy('Некорректная дата рождения'))
        return birth_date


class CommentForm(forms.ModelForm):
    """
    Форма для создания комментария.

    :attribute Meta.model: Модель, связанная с формой.
    :type Meta.model: :class:`main_app.models.Comment`
    """
    class Meta:
        """
        Мета-данные для формы.

        :attribute model: Модель, связанная с формой.
        :type model: :class:`main_app.models.Comment`
        :attribute fields: Поля формы.
        :type fields: list[str]
        :attribute widgets: Виджеты для полей.
        :type widgets: dict[str, :class:`django.forms.Widget`]
        """
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'comment-input',
                'placeholder': 'Write your comment...'
            }),
        }


class DBFileField(forms.FileField):
    """
    Поле формы для обработки файлов, преобразующее файл в словарь с метаданными.

    :attribute required: Обязательно ли поле.
    :type required: bool
    :attribute label: Метка поля.
    :type label: str
    """
    def to_python(self, data: Any) -> Optional[dict[str, Any]]:
        """
        Преобразует загруженный файл в словарь с именем, типом, данными и размером.

        :param data: Данные файла.
        :type data: Any
        :returns: Словарь с метаданными файла или None, если данные отсутствуют.
        :rtype: Optional[dict[str, Any]]
        """
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
    """
    Форма для создания поля.

    :attribute file: Поле для загрузки файла.
    :type file: :class:`main_app.forms.DBFileField`
    """
    file = DBFileField(required=False, label="Прикрепленный файл")

    cols = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        widget=forms.NumberInput(attrs={'min': 1, 'max': 20}),
        label='Количество колонок'
    )

    rows = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        widget=forms.NumberInput(attrs={'min': 1, 'max': 20}),
        label='Количество строк'
    )

    class Meta:
        """
        Мета-данные для формы.

        :attribute model: Модель, связанная с формой.
        :type model: :class:`main_app.models.Field`
        :attribute fields: Поля формы.
        :type fields: list[str]
        :attribute widgets: Виджеты для полей.
        :type widgets: dict[str, :class:`django.forms.Widget`]
        :attribute labels: Метки для полей.
        :type labels: dict[str, str]
        """
        model = Field
        fields = ['title', 'description', 'cols', 'rows']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'cols': 'Количество колонок',
            'rows': 'Количество строк',
        }


class FieldReportForm(forms.ModelForm):
    """
    Форма для подачи жалобы на поле.

    :attribute Meta.model: Модель, связанная с формой.
    :type Meta.model: :class:`main_app.models.FieldReport`
    """
    class Meta:
        """
        Мета-данные для формы.

        :attribute model: Модель, связанная с формой.
        :type model: :class:`main_app.models.FieldReport`
        :attribute fields: Поля формы.
        :type fields: list[str]
        :attribute widgets: Виджеты для полей.
        :type widgets: dict[str, :class:`django.forms.Widget`]
        """
        model = FieldReport
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
