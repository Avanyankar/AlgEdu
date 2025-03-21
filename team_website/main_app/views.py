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
    View for editing the user's profile.

    Processes the fields name, mail, agent, checks them for validity
    and saves the changes to the user's model.
    """

    model: User = User 
    fields: list[str] = ['first_name', 'email', 'age']  
    template_name: str = 'editing.html'  
    success_url: str = reverse_lazy('profile')  

    def get_object(self, queryset=None) -> User:
        """
        Returns the user object associated with the current request.

        Returns:
            User: object of the current user.
        """
        return self.request.user

    def form_valid(self, form) -> bool:
        """
        Processes a valid form.

        Args:
            form: The form with the data to update.

        Returns:
            bool: The result of processing the form.
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
        Checks the data for validity.

        Args:
            cleaned_data (dict): Cleared data from the form.

        Raises:
            ValidationError: If the data is not valid.
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
    View for displaying user profile details.

    Inherits from `DetailView' and uses the `User` model.
    Available only to authorized users thanks to `LoginRequiredMixin'.
    """

    model: User = User  
    template_name: str = 'profile.html' 
    context_object_name: str = 'user'

    def get_object(self, queryset=None) -> User:
        """
        Returns the user object associated with the current request.

        Args:
            queryset: QuerySet from which you can select an object (not used in this case).

        Returns:
            User: The object of the current user.
        """
        return self.request.user

    def get_context_data(self, **kwargs) -> dict:
        """
        Adds additional data to the template context.

        Returns:
            dict: The context with the user's object and additional data.
        """
        context: dict = super().get_context_data(**kwargs)
        context['is_profile_page'] = True
        return context


class IndexView(DetailView):
    """View for displaying the index page."""
    template_name: str = 'index.html'


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
    The view for user authorization.

    Processes username and password, authenticates the user
    and redirects to the specified page.
    """

    template_name: str = 'login.html'  
    redirect_authenticated_user: bool = True  
    success_url: str = reverse_lazy('profile') 

    def form_valid(self, form) -> bool:
        """
        Processes a valid form.

        Args:
            form: A form with authentication data.

        Returns:
            bool: The result of processing the form.
        """
        response = super().form_valid(form)
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return response

    def form_invalid(self, form) -> bool:
        """
        Handles the invalid form.

        Args:
            form: A form with authentication data.

        Returns:
            bool: The result of processing the form.
        """
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)