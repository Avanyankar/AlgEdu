from django.shortcuts import render
from django.views.generic import UpdateView, DetailView, View, CreateView
from django.urls import reverse_lazy
from .models import UserProfile, User
from .forms import UserRegistrationForm
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any

# Create your views here.

class ProfileUpdateView(UpdateView):
    """View for updating user profile information."""

    model: UserProfile = UserProfile
    fields: list[str] = ['location', 'birth_date', 'bio']
    template_name: str = 'main/editing.html'

    def get_object(self, queryset: Any = None) -> UserProfile:
        """Retrieve the user profile associated with the current user."""
        return self.request.user.userprofile

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

    def get_success_url(self) -> str:
        """Return the URL to redirect to after a successful form submission."""
        return reverse_lazy('main:profile')


class ProfileDetailView(DetailView):
    """View for displaying user profile details."""

    model: UserProfile = UserProfile
    template_name: str = 'main/profile.html'

    def get_object(self, queryset: Any = None) -> UserProfile:
        """Retrieve the user profile associated with the current user."""
        return self.request.user.userprofile


class ProfileView(View):
    """View for displaying the user's profile page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the profile page for the current user."""
        context = {
            'user': request.user
        }
        return render(request, 'main/profile.html', context)


class IndexView(View):
    """View for displaying the index page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the index page."""
        return render(request, 'main/index.html', {})


class UserRegisterView(CreateView):
    """View for user registration."""

    model: User = User
    form_class: Any = UserRegistrationForm
    template_name: str = 'accounts/register.html'
    success_url: str = reverse_lazy('login')

    def form_valid(self, form: Any) -> HttpResponse:
        """Handle valid form submission and set a success message."""
        response: HttpResponse = super().form_valid(form)
        self.request.session['success_message'] = 'Регистрация успешна'
        return response


class PosxalkoView(View):
    """View for displaying the main page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the main page."""
        return render(request, 'main.html')