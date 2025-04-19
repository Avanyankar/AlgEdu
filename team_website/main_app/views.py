from typing import Dict, Any
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, CreateView, TemplateView, ListView
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from main_app.models import User, Field, Comment, Wall, Cell, ProfileComment, FieldFile, Post, LikeField, FavoriteField, FieldReport
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django_registration.signals import user_registered
from main_app.forms import RegistrationForm, ProfileUpdateForm, FieldForm, FieldReportForm
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
    Can display both current user profile and other users' profiles.
    """
    model = User
    template_name = 'profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None) -> User:
        """
        Returns the user object based on username in URL or current user.
        """
        if 'username' in self.kwargs:
            return get_object_or_404(User, username=self.kwargs['username'])
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_profile_page'] = True
        context['is_own_profile'] = (self.object == self.request.user)


        context['profile_comments'] = ProfileComment.objects.filter(
            profile=self.object
        ).select_related('author').order_by('-created_at')

        return context


@login_required
def add_profile_comment(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        text = request.POST.get('comment_text', '').strip()
        if text:
            ProfileComment.objects.create(
                profile=profile_user,
                author=request.user,
                text=text
            )
            messages.success(request, 'Комментарий добавлен')
    return redirect('profile_view', username=username)



@login_required
def delete_profile_comment(request, comment_id):
    comment = get_object_or_404(ProfileComment, id=comment_id)



    if request.user == comment.profile or request.user == comment.author or request.user.is_superuser:
        comment.delete()
        messages.success(request, 'Комментарий удален')

    return redirect('profile')

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

class ReportFieldView(LoginRequiredMixin, CreateView):
    """
    View for reporting inappropriate field content.
    
    Processes the report reason and description,
    validates them and creates a new FieldReport instance.
    """
    
    model: FieldReport = FieldReport
    form_class = FieldReportForm
    template_name: str = 'report_field.html'
    
    def get_success_url(self) -> str:
        """
        Returns the URL to redirect to after successful report.
        
        Returns:
            str: URL of the reported field.
        """
        return reverse_lazy('index')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Adds the field object to the template context.
        
        Returns:
            Dict[str, Any]: Context with field and form.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        field = get_object_or_404(Field, id=self.kwargs['field_id'])
        context['field'] = field
        
        context['existing_report'] = FieldReport.objects.filter(
            field_id=field.id,
            user=self.request.user,
            is_resolved=False
        ).first()
        
        return context
    
    def form_valid(self, form) -> HttpResponse:
        """
        Processes a valid form and creates a report.
        
        Args:
            form: The filled report form.
            
        Returns:
            HttpResponse: Redirect to success URL.
        """
        try:
            self.validate_report(form.cleaned_data)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)
        
        report = form.save(commit=False)
        report.field = get_object_or_404(Field, id=self.kwargs['field_id'])
        report.user = self.request.user
        report.save()
        
        messages.success(self.request, 'Жалоба успешно отправлена!')
        return super().form_valid(form)
    
    def validate_report(self, cleaned_data: Dict[str, Any]) -> None:
        """
        Validates the report data.
        
        Args:
            cleaned_data: Dictionary with cleaned form data.
            
        Raises:
            ValidationError: If data is invalid.
        """
        reason = cleaned_data.get('reason')
        description = cleaned_data.get('description')
        
        if not reason:
            raise ValidationError('Укажите причину жалобы.')
        
        if reason == 'other' and not description:
            raise ValidationError('Для причины "Другое" необходимо описание.')
        
        existing_report = FieldReport.objects.filter(
            field_id=self.kwargs['field_id'],
            user=self.request.user,
            is_resolved=False
        ).exists()
        
        if existing_report:
            raise ValidationError('Вы уже отправляли жалобу на это поле.')


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


class AboutPageView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['company_name'] = "Моя Компания"
        context['foundation_year'] = "2010"
        context['team_size'] = "50"
        context['team_members'] = [
            {
                'name': 'Иван Иванов',
                'position': 'Основатель и CEO',
                'bio': 'Иван основал компанию в 2010 с видением создания инновационных решений для бизнеса.',
                'image': 'team-member1.jpg'
            },
            {
                'name': 'Алексей Петров',
                'position': 'Технический директор',
                'bio': 'Алексей присоединился к команде в 2012 и возглавляет техническое развитие компании.',
                'image': 'team-member2.jpg'
            }
        ]
        context['contact_info'] = {
            'address': 'ул. Примерная, 123, Москва',
            'phone': '+7 (123) 456-78-90',
            'email': 'info@mycompany.com',
            'working_hours': 'Пн-Пт: 9:00-18:00'
        }
        return context


class GoalsPageView(TemplateView):
    template_name = 'goals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['mission'] = "Мы стремимся создавать инновационные решения, которые делают бизнес эффективнее."
        context['goals'] = [
            {
                'title': 'Глобальное присутствие',
                'description': 'Расширение нашей деятельности на 5 новых рынков к 2025 году.',
                'icon': '🌍'
            },
            {
                'title': 'Инновации',
                'description': 'Разработка 10 новых технологических решений ежегодно.',
                'icon': '💡'
            },
            {
                'title': 'Развитие команды',
                'description': 'Инвестиции в профессиональный рост наших сотрудников.',
                'icon': '👥'
            },
            {
                'title': 'Устойчивое развитие',
                'description': 'Достижение углеродной нейтральности к 2030 году.',
                'icon': '♻️'
            }
        ]
        context['metrics'] = [
            {
                'title': 'Удовлетворенность клиентов',
                'target': '95% положительных отзывов к концу 2025 года',
                'progress': 87
            },
            {
                'title': 'Рост компании',
                'target': 'Увеличение выручки на 30% ежегодно',
                'progress': 25
            },
            {
                'title': 'Экологические инициативы',
                'target': 'Снижение углеродного следа на 40% к 2026 году',
                'progress': 15
            }
        ]
        return context

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
        
        if len(text) > 1000:
            return JsonResponse({'error': 'Comment is too long (max 1000 chars)'}, status=400)

        field = get_object_or_404(Field, id=pk)
        comment = Comment.objects.create(
            field=field,
            author=request.user,
            text=text
        )

        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'author': comment.author.username,
            'text': comment.text,
            'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M") if comment.created_at else None
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error in add_comment: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


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
    phrases = ["Goida", "1488", "OGbolshieyayca", "tarZan pidor", "Ave Python", "meow"]
    phrase_data = []
    for _ in range(30):
        phrase_data.append({
            'text': random.choice(phrases),
            'x': random.randint(5, 95),
            'y': random.randint(5, 95),
            'size': random.randint(16, 32),
            'color': f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})",
            'speed': random.uniform(0.01, 1)
        })

    context = {
        'phrases': phrase_data,
        'image_url': 'meow.jpg'
    }
    return render(request, 'spinning_image.html', context)
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('login')


class FieldCreateView(LoginRequiredMixin, CreateView):
    model = Field
    form_class = FieldForm
    template_name = 'create_field.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        field = form.save(commit=False)
        field.user = self.request.user

        file_data = form.cleaned_data.get('file')
        if file_data:
            field_file = FieldFile.objects.create(
                name=file_data['name'],
                content_type=file_data['content_type'],
                data=file_data['data'],
                size=file_data['size']
            )
            field.file = field_file

        field.save()
        return super().form_valid(form)
def download_file(request, pk):
    field_file = get_object_or_404(FieldFile, pk=pk)
    response = HttpResponse(field_file.data, content_type=field_file.content_type)
    response['Content-Disposition'] = f'attachment; filename="{field_file.name}"'
    return response