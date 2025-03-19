from typing import Dict, Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import User


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View для редактирования профиля пользователя.

    Обрабатывает поля name, mail, age, проверяет их на валидность
    и сохраняет изменения в модели пользователя.
    """

    model: User = User 
    fields: list[str] = ['first_name', 'email', 'age']  
    template_name: str = 'main/editing.html'  
    success_url: str = reverse_lazy('profile')  

    def get_object(self, queryset=None) -> User:
        """
        Возвращает объект пользователя, связанный с текущим запросом.

        Returns:
            User: Объект текущего пользователя.
        """
        return self.request.user

    def form_valid(self, form) -> bool:
        """
        Обрабатывает валидную форму.

        Args:
            form: Форма с данными для обновления.

        Returns:
            bool: Результат обработки формы.
        """
        try:
            self.validate_data(form.cleaned_data)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

        response = super().form_valid(form)
        messages.success(self.request, 'Профиль успешно обновлён!')
        return response

    def validate_data(self, cleaned_data: dict) -> None: 
        """
        Проверяет данные на валидность.

        Args:
            cleaned_data (dict): Очищенные данные из формы.

        Raises:
            ValidationError: Если данные невалидны.
        """
        name = cleaned_data.get('first_name')
        email = cleaned_data.get('email')
        age = cleaned_data.get('age')

        if not name:
            raise ValidationError('Имя не может быть пустым.')
        if not email or '@' not in email:
            raise ValidationError('Введите корректный email.')
        if age and (age < 0 or age > 120):
            raise ValidationError('Возраст должен быть от 0 до 120 лет.')


class ProfileView(LoginRequiredMixin, DetailView):
    """
    View для отображения деталей профиля пользователя.

    Наследуется от `DetailView` и использует модель `User`.
    Доступен только для авторизованных пользователей благодаря `LoginRequiredMixin`.
    """

    model: User = User  
    template_name: str = 'main/profile.html' 
    context_object_name: str = 'user'

    def get_object(self, queryset=None) -> User:
        """
        Возвращает объект пользователя, связанный с текущим запросом.

        Args:
            queryset: QuerySet, из которого можно выбрать объект (не используется в данном случае).

        Returns:
            User: Объект текущего пользователя.
        """
        return self.request.user

    def get_context_data(self, **kwargs) -> dict:
        """
        Добавляет дополнительные данные в контекст шаблона.

        Returns:
            dict: Контекст с объектом пользователя и дополнительными данными.
        """
        context: dict = super().get_context_data(**kwargs)
        context['is_profile_page'] = True
        return context


class IndexView(DetailView):
    """View for displaying the index page."""
    template_name: str = 'main/index.html'


class UserRegisterView(CreateView):
    """View for user registration."""

    model: User = User
    form_class: Any = None  # TODO: registration form
    template_name: str = 'accounts/register.html'
    success_url: str = reverse_lazy('login')

    def form_valid(self, form: Any) -> HttpResponse:
        """Handle valid form submission and set a success message."""
        response: HttpResponse = super().form_valid(form)
        self.request.session['success_message'] = 'Регистрация успешна'
        return response


class UserLoginView(LoginView):
    """
    View для авторизации пользователя.

    Обрабатывает username и password, аутентифицирует пользователя
    и перенаправляет на указанную страницу.
    """

    template_name: str = 'main/login.html'  
    redirect_authenticated_user: bool = True  
    success_url: str = reverse_lazy('profile') 

    def form_valid(self, form) -> bool:
        """
        Обрабатывает валидную форму.

        Args:
            form: Форма с данными для аутентификации.

        Returns:
            bool: Результат обработки формы.
        """
        response = super().form_valid(form)
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return response

    def form_invalid(self, form) -> bool:
        """
        Обрабатывает невалидную форму.

        Args:
            form: Форма с данными для аутентификации.

        Returns:
            bool: Результат обработки формы.
        """
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)