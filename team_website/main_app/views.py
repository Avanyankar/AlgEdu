from typing import Dict, Any
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, CreateView, TemplateView, ListView
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from main_app.models import User, Field, Post, LikeField, FavoriteField
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django_registration.signals import user_registered
from .forms import RegistrationForm, ProfileUpdateForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from .models import Field, LikeField, FavoriteField

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for editing the user's profile.

    Processes the fields name, mail, agent, checks them for validity
    and saves the changes to the user's model.
    """

    model: User = User
    form_class = ProfileUpdateForm
    template_name: str = 'editing.html'
    success_url: str = reverse_lazy('profile')

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
    template_name: str = 'post_detail.html'
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
    form_class = RegistrationForm
    template_name: str = 'register.html'
    success_url: str = reverse_lazy('login')

    def form_valid(self, form):
        """Processing a valid registration form"""
        user = form.save()

        user_registered.send(
            sender=self.__class__,
            user=user,
            request=self.request
        )
        
        login(self.request, user)
        
        messages.success(self.request, 'Регистрация успешно завершена!')
        
        return super().form_valid(form)
    
    def register(self, form):
        user = form.save()
        
        user_registered.send(
            sender=self.__class__,
            user=user,
            request=self.request
        )
        
        return user



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


class CardView(ListView):
    """
    A borderline-retarded implementation of a ListView that pretends to be a DetailView.
    Despite inheriting from ListView (which is meant for multiple objects),
    this dumbass view only returns a single object filtered by PK.

    Warning:
        This is a fucking abomination because:
        1. Using ListView for single object display is like using a chainsaw to butter bread
        2. The queryset filtering by PK defeats the whole purpose of ListView
        3. You'll confuse the shit out of any developer who sees this (including future you)

    Typical usage:
        Don't use this shit. Use DetailView instead unless you enjoy pain.

    Attributes:
        template_name (str): The template that will render this trainwreck (card.html)
        context_object_name (str): The dumb name you'll use in template to access ONE object (Field)

    Methods:
        get_queryset: Returns a "queryset" containing exactly one object (because fuck conventions)
        get_context_data: Does absolutely nothing useful (classic)
    """

    template_name = 'card.html'
    context_object_name = 'Field'

    def get_queryset(self):
        """
        The most pointless ListView queryset in existence.
        Filters for exactly one object, making this whole class completely fucking useless.

        Returns:
            QuerySet: A queryset containing either:
                - One Field object (if PK exists)
                - Fuck-all (if PK doesn't exist)
        """
        return Field.objects.filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        An empty shell of a method that exists solely to:
        1. Pretend this class does something meaningful
        2. Waste CPU cycles calling super() for no reason
        3. Make junior developers question their career choices

        Returns:
            dict: The same context you'd get without this method. Groundbreaking.
        """
        context = super().get_context_data(**kwargs)
        return context


@csrf_exempt
@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': post.likes.count()})


@login_required
def favorite_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user in post.favorites.all():
        post.favorites.remove(request.user)
        favorited = False
    else:
        post.favorites.add(request.user)
        favorited = True
    return JsonResponse({'favorited': favorited})

@require_GET
@login_required
def get_user_fields(request):
    field_type = request.GET.get('type', 'my')
    user = request.user
    
    if field_type == 'my':
        fields = Field.objects.filter(user=user)
    elif field_type == 'liked':
        fields = Field.objects.filter(likefield__user=user)
    elif field_type == 'favorites':
        fields = Field.objects.filter(favoritefield__user=user)
    
    serialized_fields = [{
        'id': field.id,
        'title': field.title,
        'description': field.description[:100] + '...' if field.description else '',
        # TODO: 'image_url': field.image.url if field.image else '/static/default_field.jpg',
        'created_at': field.created_at.strftime("%d.%m.%Y")
    } for field in fields]
    
    return JsonResponse({'fields': serialized_fields})