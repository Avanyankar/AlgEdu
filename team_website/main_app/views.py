from typing import Dict, Any
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, CreateView, TemplateView, ListView
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from main_app.models import User, Field, Comment, Wall, Cell
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django_registration.signals import user_registered
from .forms import RegistrationForm, ProfileUpdateForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
import json

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

    model = Field
    template_name = 'index.html'
    context_object_name = 'user'

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
        context = super().get_context_data(**kwargs)
        context['fields'] = Field.objects.all()
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
        success_url (str): The URL to redirect to after a   successful loginsddssd.
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

        # Создаем клетки, если их еще нет
        if not field.cells.exists():
            self.create_cells(field)

        context.update({
            'is_liked': field.likes.filter(
                id=self.request.user.id).exists() if self.request.user.is_authenticated else False,
            'is_favorited': field.favorites.filter(
                id=self.request.user.id).exists() if self.request.user.is_authenticated else False,
            'cols': field.cols,
            'rows': field.rows,
        })
        return context

    def create_cells(self, field):
        """Создает клетки для поля при первом обращении"""
        cells = []
        for x in range(field.cols):
            for y in range(field.rows):
                cells.append(Cell(field=field, x=x, y=y))
        Cell.objects.bulk_create(cells)

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

def search_fields(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    fields = Field.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    ).values('id', 'title', 'description', 'created_at')
    
    results = []
    for field in fields:
        field['created_at'] = field['created_at'].strftime('%d.%m.%Y')
        results.append(field)
    
    return JsonResponse({'results': results})


@require_POST
@login_required
def toggle_like(request, pk):
    field = Field.objects.get(id=pk)
    if request.user in field.likes.all():
        field.likes.remove(request.user)
        is_liked = False
    else:
        field.likes.add(request.user)
        is_liked = True
    return JsonResponse({
        'is_liked': is_liked,
        'likes_count': field.likes.count()
    })


@require_POST
@login_required
def toggle_favorite(request, pk):
    field = Field.objects.get(id=pk)
    if request.user in field.favorites.all():
        field.favorites.remove(request.user)
        is_favorited = False
    else:
        field.favorites.add(request.user)
        is_favorited = True
    return JsonResponse({
        'is_favorited': is_favorited
    })


@require_POST
@login_required
def add_comment(request, pk):
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()

        if not text:
            return JsonResponse({'error': 'Comment text cannot be empty'}, status=400)

        field = Field.objects.get(id=pk)
        comment = Comment.objects.create(
            field=field,
            author=request.user,
            text=text
        )

        return JsonResponse({
            'success': True,
            'author': comment.author.username,
            'text': comment.text,
            'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M")
        })

    except Field.DoesNotExist:
        return JsonResponse({'error': 'Field not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def field_detail(request, pk):
    field = Field.objects.get(id=pk)
    is_liked = request.user.is_authenticated and request.user in field.likes.all()
    is_favorited = request.user.is_authenticated and request.user in field.favorites.all()

    return render(request, 'your_app/field_detail.html', {
        'field': field,
        'is_liked': is_liked,
        'is_favorited': is_favorited
    })


@require_POST
@login_required
def toggle_comment_like(request, pk):
    try:
        comment = Comment.objects.get(id=pk)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            is_liked = False
        else:
            comment.likes.add(request.user)
            is_liked = True

        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': comment.likes.count()
        })
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Комментарий не найден'}, status=404)


@require_POST
@login_required
def report_comment(request, pk):
    try:
        comment = Comment.objects.get(id=pk)
        if request.user not in comment.reports.all():
            comment.reports.add(request.user)

        return JsonResponse({
            'success': True,
            'reports_count': comment.reports.count()
        })
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Комментарий не найден'}, status=404)


@require_POST
@login_required
def add_wall(request):
    """Добавление новой стены"""
    try:
        data = json.loads(request.body)
        field_id = data.get('field_id')
        x = int(data.get('x'))
        y = int(data.get('y'))
        width = int(data.get('width', 1))
        height = int(data.get('height', 1))

        field = Field.objects.get(id=field_id)

        # Проверка, что стена не выходит за границы
        if x + width > field.cols or y + height > field.rows:
            return JsonResponse({'error': 'Wall exceeds field boundaries'}, status=400)

        wall = Wall.objects.create(
            field=field,
            x=x,
            y=y,
            width=width,
            height=height,
            created_by=request.user
        )

        return JsonResponse({
            'success': True,
            'wall': {
                'id': wall.id,
                'x': wall.x,
                'y': wall.y,
                'width': wall.width,
                'height': wall.height
            }
        })

    except Field.DoesNotExist:
        return JsonResponse({'error': 'Field not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@login_required
def remove_wall(request, pk):
    """Удаление стены"""
    try:
        wall = Wall.objects.get(id=pk)
        if wall.created_by != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        wall.delete()
        return JsonResponse({'success': True})

    except Wall.DoesNotExist:
        return JsonResponse({'error': 'Wall not found'}, status=404)


def get_field_state(request, pk):
    """Получение текущего состояния поля"""
    try:
        field = Field.objects.get(id=pk)
        walls = Wall.objects.filter(field=field).values('id', 'x', 'y', 'width', 'height')

        return JsonResponse({
            'cols': field.cols,
            'rows': field.rows,
            'walls': list(walls)
        })

    except Field.DoesNotExist:
        return JsonResponse({'error': 'Field not found'}, status=404)


import random


def spinning_image_view(request):
    phrases = ["Goida", "1488", "OGbolshieyayca", "tarZan pidor"]

    # Создаем 20 фраз со случайными параметрами
    phrase_data = []
    for _ in range(20):
        phrase_data.append({
            'text': random.choice(phrases),
            'x': random.randint(5, 95),
            'y': random.randint(5, 95),
            'size': random.randint(16, 32),
            'color': f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})",
            'speed': random.uniform(0.5, 2)
        })

    context = {
        'phrases': phrase_data,
        'image_url': 'meow.jpg'  # Ваше изображение
    }
    return render(request, 'spinning_image.html', context)

def help():
    pass