from typing import Dict, Any
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, UpdateView, DetailView, CreateView, TemplateView, ListView
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from django.contrib import messages
from main_app.models import User, Field, Comment, Post, LikeField, FavoriteField, Field, FieldReport
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django_registration.signals import user_registered
from .forms import RegistrationForm, ProfileUpdateForm, FieldReportForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


import json


class FieldListView(ListView):
    model = Field
    template_name = 'fields/list.html'
    context_object_name = 'fields'

    def get_queryset(self):
        return Field.objects.filter(is_blocked=False).order_by('-created_at')


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

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_blocked:
            raise Http404("Карта заблокирована и недоступна для просмотра")
        return obj


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


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('login')
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class ModerationPanelView(StaffRequiredMixin, TemplateView):
    template_name = 'moderation/panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['field_reports'] = FieldReport.objects.filter(
            is_resolved=False
        ).select_related('field', 'user')


        context['blocked_fields'] = Field.objects.filter(
            is_blocked=True
        ).order_by('-updated_at')[:10]

        context['blocked_comments'] = Comment.objects.filter(
            is_blocked=True
        ).order_by('-created_at')[:10]

        return context


class ResolveCommentReportView(StaffRequiredMixin, View):

    def get(self, request, report_id):
        report = get_object_or_404(ReportComment, id=report_id)
        return render(request, 'moderation/resolve_comment.html', {
            'report': report,
        })

    def post(self, request, report_id):
        report = get_object_or_404(ReportComment, id=report_id)
        action = request.POST.get('action')

        if action == 'block':
            report.comment.block()
            report.status = 'approved'
            messages.success(request, 'Комментарий заблокирован')
        elif action == 'ignore':
            report.status = 'rejected'
            messages.info(request, 'Жалоба отклонена')

        report.is_resolved = True
        report.save()
        return redirect('moderation_panel')

class ResolveFieldReportView(StaffRequiredMixin, View):

    def get(self, request, report_id):
        report = get_object_or_404(FieldReport, id=report_id)
        return render(request, 'moderation/resolve_field.html', {
            'report': report,
        })

    def post(self, request, report_id):
        report = get_object_or_404(FieldReport, id=report_id)
        action = request.POST.get('action')

        if action == 'block':
            report.field.block()
            report.status = 'approved'
            messages.success(request, 'Карта заблокирована')
        elif action == 'ignore':
            report.status = 'rejected'
            messages.info(request, 'Жалоба отклонена')

        report.is_resolved = True
        report.save()
        return redirect('moderation_panel')


class UnblockContentView(StaffRequiredMixin, View):

    def post(self, request, content_type, content_id):
        if content_type == 'field':
            obj = get_object_or_404(Field, id=content_id)
            obj.unblock()
            messages.success(request, 'Карта разблокирована')
        elif content_type == 'comment':
            obj = get_object_or_404(Comment, id=content_id)
            obj.unblock()
            messages.success(request, 'Комментарий разблокирован')
        else:
            messages.error(request, 'Неверный тип контента')
            return redirect('moderation_panel')

        return redirect('moderation_panel')


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


@staff_member_required
def moderation_panel(request):
    reports = FieldReport.objects.filter(status='pending').select_related('field', 'user')
    return render(request, 'moderation/moderation_panel.html', {
        'reports': reports
    })

@staff_member_required
def block_content(request, content_type, content_id):
    content_models = {
        'field': Field,
        'comment': Comment,
        'user': request.user.__class__  
    }
    
    if content_type not in content_models:
        raise Http404("Тип контента не поддерживается")
    
    model = content_models[content_type]
    item = get_object_or_404(model, pk=content_id)
    item.is_blocked = True
    item.save()
    messages.success(request, f'{content_type.capitalize()} успешно заблокирован')
    return redirect(reverse_lazy('hidden-admin-panel'))