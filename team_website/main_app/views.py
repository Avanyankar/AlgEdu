from typing import Dict, Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import User


class ProfileUpdateView(UpdateView):
    """View for updating user profile information."""

    model: User = User
    fields: list[str] = ['location', 'birth_date', 'bio']
    template_name: str = 'main/editing.html'

    def get_object(self, queryset: Any = None) -> User:
        """Retrieve the user profile associated with the current user."""
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add the user profile to the context data."""
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context

    def form_valid(self, form: Any) -> HttpResponse:
        """Handle valid form submission and set a success message."""
        response: HttpResponse = super().form_valid(form)
        self.request.session['success_message'] = 'Успешное изменение профиля'
        return response


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
