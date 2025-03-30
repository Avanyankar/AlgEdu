from typing import Dict, Any
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, CreateView, TemplateView
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from main_app.models import User, Field
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Count

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for editing the user's profile.

    Processes the fields name, mail, agent, checks them for validity
    and saves the changes to the user's model.
    """

    model: User = User
    fields: list[str] = ['first_name', 'last_name', 'bio', 'birth_date', 'location']
    template_name: str = 'editing.html'
    success_url: str = 'profile'

    def get_object(self, queryset=None) -> User:
        """
        Returns the user object associated with the current request.

        Args:
            queryset: QuerySet from which you can select an object (not used in this case).

        Returns:
            User: The object of the current user.
        """
        return self.request.user

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Adds additional data to the template context.

        Returns:
            Dict[str, Any]: The context with the user's object and additional data.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form) -> HttpResponse:
        """
        Processes a valid form.

        Args:
            form: The form with the data to update.

        Returns:
            HttpResponse: The result of processing the form.
        """
        try:
            self.validate_data(form.cleaned_data)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

        response: HttpResponse = super().form_valid(form)
        messages.success(self.request, 'Профиль успешно обновлён!')
        return response

    def validate_data(self, cleaned_data: Dict[str, Any]) -> None:
        """
        Checks the data for validity.

        Args:
            cleaned_data (Dict[str, Any]): Cleared data from the form.

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

    Inherits from `DetailView` and uses the `User` model.
    Available only to authorized users thanks to `LoginRequiredMixin`.
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

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Adds additional data to the template context.

        Returns:
            Dict[str, Any]: The context with the user's object and additional data.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['is_profile_page'] = True
        return context


class IndexView(DetailView):
    """
    View for displaying the index page.
    """

    model: Field = Field
    template_name: str = 'index.html'
    context_object_name: str = 'user'

    def get_object(self) -> User:
        """
        Returns the user object associated with the current request.

        Returns:
            User: The object of the current user.
        """
        return self.request.user

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Adds additional data to the template context.

        Returns:
            Dict[str, Any]: The context with the user's object and additional data.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['fields'] = self.model.objects.all()
        return context


class UserRegisterView(CreateView):
    """
    View for user registration.

    This view handles the registration process, including form validation,
    password hashing, and redirection after successful registration.

    Attributes:
        model (User): The user model used for registration.
        fields (list[str]): The fields to include in the registration form.
        template_name (str): The path to the template used for rendering the registration page.
        success_url (str): The URL to redirect to after a successful registration.
    """

    model: User = User
    fields: list[str] = ['username', 'password', 'email']
    template_name: str = 'register.html'
    success_url: str = reverse_lazy('login')

    def form_valid(self, form: Any) -> HttpResponse:
        """
        Handle valid form submission, hash the password, and save the user.

        Args:
            form: The form with the registration data.

        Returns:
            HttpResponse: The result of processing the form.
        """
        user: User = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(self.request, 'Регистрация успешна!')
        return super().form_valid(form)



class UserLoginView(LoginView):
    """
    View for user authorization.

    This view handles the login process, including form validation,
    authentication, and redirection after successful login.

    Attributes:
        template_name (str): The path to the template used for rendering the login page.
        form_class (type[AuthenticationForm]): The form class used for authentication.
        redirect_authenticated_user (bool): If True, authenticated users will be redirected
                                            to the success URL.
        success_url (str): The URL to redirect to after a successful login.
    """

    template_name: str = 'login.html'
    form_class: type[AuthenticationForm] = AuthenticationForm
    redirect_authenticated_user: bool = True
    success_url: str = reverse_lazy('profile')

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        """
        Processes a valid form and logs in the user.

        Args:
            form (AuthenticationForm): The form containing validated authentication data.

        Returns:
            HttpResponse: The response after successful form processing.
        """
        response: HttpResponse = super().form_valid(form)
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return response

    def form_invalid(self, form: AuthenticationForm) -> HttpResponse:
        """
        Handles the case when the form is invalid.

        Args:
            form (AuthenticationForm): The form containing invalid authentication data.

        Returns:
            HttpResponse: The response after handling the invalid form.
        """
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)


class NotFoundView(TemplateView):
    """
    View for displaying the 404 error page.
    """

    template_name: str = '404.html'

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Adds additional data to the template context.

        Returns:
            Dict[str, Any]: The context with additional data.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        return context


class FieldDetailView(DetailView):
    model = Field
    template_name = 'card_detail.html'
    context_object_name = 'field'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        field = self.get_object()
        context['is_liked'] = field.likes.filter(id=self.request.user.id).exists() if self.request.user.is_authenticated else False
        context['is_favorited'] = field.favorites.filter(id=self.request.user.id).exists() if self.request.user.is_authenticated else False
        return context
from django.views.decorators.http import require_POST
@require_POST
@login_required
def toggle_like(request, pk):
    field = Field.objects.get(pk=pk)
    if field.likes.filter(id=request.user.id).exists():
        field.likes.remove(request.user)
        is_liked = False
    else:
        field.likes.add(request.user)
        is_liked = True
    return JsonResponse({'is_liked': is_liked, 'likes_count': field.likes.count()})

@require_POST
@login_required
def toggle_favorite(request, pk):
    field = Field.objects.get(pk=pk)
    if field.favorites.filter(id=request.user.id).exists():
        field.favorites.remove(request.user)
        is_favorited = False
    else:
        field.favorites.add(request.user)
        is_favorited = True
    return JsonResponse({'is_favorited': is_favorited})