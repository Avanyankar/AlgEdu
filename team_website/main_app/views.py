"""
Django представления для обработки аутентификации пользователей, управления профилем,
операций с полями и задач модерации.

Этот модуль содержит представления на основе классов и функций для основного приложения,
включая регистрацию пользователей, вход в систему, обновление профиля, создание и управление
полями, обработку комментариев и модерацию контента.

:mod:`main_app.views`
"""

import json
import logging
from typing import Dict, Any, Optional, List
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import HttpResponse, Http404, JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import View, UpdateView, DetailView, CreateView, TemplateView, ListView
from django_registration.signals import user_registered
from main_app.forms import RegistrationForm, ProfileUpdateForm, FieldForm, FieldReportForm
from main_app.models import User, Field, Comment, Wall, Cell, ProfileComment, FieldFile, FieldReport, ReportComment

logger: logging.Logger = logging.getLogger(__name__)

class FieldListView(ListView):
    """
    Представление для отображения списка полей.

    :attribute model: Модель, используемая для списка.
    :type model: :class:`main_app.models.Field`
    :attribute template_name: Шаблон для отображения списка.
    :type template_name: str
    :attribute context_object_name: Имя, используемое для списка полей в контексте шаблона.
    :type context_object_name: str
    """
    model: Field = Field
    template_name: str = 'fields/list.html'
    context_object_name: str = 'fields'

    def get_queryset(self) -> QuerySet[Field]:
        """
        Возвращает набор данных с незаблокированными полями, отсортированными по дате создания.

        :returns: Набор данных с полями.
        :rtype: :class:`django.db.models.QuerySet`[:class:`main_app.models.Field`]
        """
        return Field.objects.filter(is_blocked=False).order_by('-created_at')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля пользователя.

    Обрабатывает поля имени, электронной почты, возраста, проверяет их на валидность
    и сохраняет изменения в модели пользователя.

    :attribute model: Модель пользователя.
    :type model: :class:`main_app.models.User`
    :attribute form_class: Форма для обновления профиля.
    :type form_class: :class:`main_app.forms.ProfileUpdateForm`
    :attribute template_name: Шаблон для страницы редактирования.
    :type template_name: str
    :attribute success_url: URL для перенаправления после успешного обновления.
    :type success_url: str
    """
    model: User = User
    form_class: ProfileUpdateForm = ProfileUpdateForm
    template_name: str = 'editing.html'
    success_url: str = reverse_lazy('profile')

    def get_object(self, queryset: Optional[QuerySet[User]] = None) -> User:
        """
        Возвращает объект пользователя, связанный с текущим запросом.

        :param queryset: Набор данных для выборки объекта (не используется).
        :type queryset: Optional[:class:`django.db.models.QuerySet`[:class:`main_app.models.User`]]
        :returns: Объект текущего пользователя.
        :rtype: :class:`main_app.models.User`
        """
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет дополнительные данные в контекст шаблона.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с объектом пользователя и дополнительными данными.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form: ProfileUpdateForm) -> HttpResponse:
        """
        Обрабатывает валидную форму.

        :param form: Форма с данными для обновления.
        :type form: :class:`main_app.forms.ProfileUpdateForm`
        :returns: Результат обработки формы.
        :rtype: :class:`django.http.HttpResponse`
        :raises ValidationError: Если данные формы невалидны.
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
        Проверяет данные на валидность.

        :param cleaned_data: Очищенные данные из формы.
        :type cleaned_data: Dict[str, Any]
        :raises ValidationError: Если данные невалидны.
        """
        name: Optional[str] = cleaned_data.get('first_name')
        email: Optional[str] = cleaned_data.get('email')
        age: Optional[int] = cleaned_data.get('age')
        if not name:
            raise ValidationError('Имя не может быть пустым.')
        if not email or '@' not in email:
            raise ValidationError('Введите корректный email.')
        if age and (age < 0 or age > 120):
            raise ValidationError('Возраст должен быть от 0 до 120 лет.')

class ProfileView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения деталей профиля пользователя.
    Может отображать как профиль текущего пользователя, так и профили других пользователей.

    :attribute model: Модель пользователя.
    :type model: :class:`main_app.models.User`
    :attribute template_name: Шаблон для отображения профиля.
    :type template_name: str
    :attribute context_object_name: Имя объекта профиля в контексте шаблона.
    :type context_object_name: str
    """
    model: User = User
    template_name: str = 'profile.html'
    context_object_name: str = 'profile_user'

    def get_object(self, queryset: Optional[QuerySet[User]] = None) -> User:
        """
        Возвращает объект пользователя на основе имени пользователя в URL или текущего пользователя.

        :param queryset: Набор данных для выборки объекта (не используется).
        :type queryset: Optional[:class:`django.db.models.QuerySet`[:class:`main_app.models.User`]]
        :returns: Объект пользователя.
        :rtype: :class:`main_app.models.User`
        """
        if 'username' in self.kwargs:
            return get_object_or_404(User, username=self.kwargs['username'])
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет дополнительные данные в контекст шаблона.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с дополнительными данными.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['is_profile_page'] = True
        context['is_own_profile'] = self.object == self.request.user
        context['profile_comments'] = ProfileComment.objects.filter(
            profile=self.object
        ).select_related('author').order_by('-created_at')
        return context

@login_required
def add_profile_comment(request: HttpRequest, username: str) -> HttpResponse:
    """
    Добавляет комментарий к профилю пользователя.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param username: Имя пользователя, к профилю которого добавляется комментарий.
    :type username: str
    :returns: Перенаправление на страницу профиля.
    :rtype: :class:`django.http.HttpResponse`
    """
    profile_user: User = get_object_or_404(User, username=username)
    if request.method == 'POST':
        text: str = request.POST.get('comment_text', '').strip()
        if text:
            ProfileComment.objects.create(
                profile=profile_user,
                author=request.user,
                text=text
            )
            messages.success(request, 'Комментарий добавлен')
    return redirect('profile_view', username=username)

@login_required
def delete_profile_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    """
    Удаляет комментарий к профилю.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param comment_id: ID комментария.
    :type comment_id: int
    :returns: Перенаправление на страницу профиля.
    :rtype: :class:`django.http.HttpResponse`
    """
    comment: ProfileComment = get_object_or_404(ProfileComment, id=comment_id)
    if (request.user == comment.profile or request.user == comment.author
            or request.user.is_superuser):
        comment.delete()
        messages.success(request, 'Комментарий удален')
    return redirect('profile')

class IndexView(DetailView):
    """
    Представление для отображения главной страницы.

    :attribute model: Модель поля.
    :type model: :class:`main_app.models.Field`
    :attribute template_name: Шаблон для главной страницы.
    :type template_name: str
    :attribute context_object_name: Имя объекта в контексте шаблона.
    :type context_object_name: str
    """
    model: Field = Field
    template_name: str = 'index.html'
    context_object_name: str = 'user'

    def get_object(self) -> User:
        """
        Возвращает объект пользователя, связанный с текущим запросом.

        :returns: Объект текущего пользователя.
        :rtype: :class:`main_app.models.User`
        """
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет дополнительные данные в контекст шаблона.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с объектом пользователя и дополнительными данными.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['fields'] = Field.objects.all()
        return context

class UserRegisterView(CreateView):
    """
    Представление для регистрации пользователя.

    Обрабатывает процесс регистрации, включая валидацию формы,
    хеширование пароля и перенаправление после успешной регистрации.

    :attribute model: Модель пользователя.
    :type model: :class:`main_app.models.User`
    :attribute form_class: Форма для регистрации.
    :type form_class: :class:`main_app.forms.RegistrationForm`
    :attribute template_name: Шаблон для страницы регистрации.
    :type template_name: str
    :attribute success_url: URL для перенаправления после успешной регистрации.
    :type success_url: str
    """
    model: User = User
    form_class: RegistrationForm = RegistrationForm
    template_name: str = 'register.html'
    success_url: str = reverse_lazy('login')

    def form_valid(self, form: RegistrationForm) -> HttpResponse:
        """
        Обрабатывает валидную форму регистрации.

        :param form: Форма регистрации.
        :type form: :class:`main_app.forms.RegistrationForm`
        :returns: Результат обработки формы.
        :rtype: :class:`django.http.HttpResponse`
        """
        user: User = form.save()
        user_registered.send(
            sender=self.__class__,
            user=user,
            request=self.request
        )
        login(self.request, user)
        messages.success(self.request, 'Регистрация успешно завершена!')
        return super().form_valid(form)

    def register(self, form: RegistrationForm) -> User:
        """
        Регистрирует пользователя.

        :param form: Форма регистрации.
        :type form: :class:`main_app.forms.RegistrationForm`
        :returns: Зарегистрированный пользователь.
        :rtype: :class:`main_app.models.User`
        """
        user: User = form.save()
        user_registered.send(
            sender=self.__class__,
            user=user,
            request=self.request
        )
        return user

class UserLoginView(LoginView):
    """
    Представление для аутентификации пользователя.

    Обрабатывает процесс входа в систему, включая валидацию формы,
    аутентификацию и перенаправление после успешного входа.

    :attribute template_name: Шаблон для страницы входа.
    :type template_name: str
    :attribute form_class: Форма для аутентификации.
    :type form_class: :class:`django.contrib.auth.forms.AuthenticationForm`
    :attribute redirect_authenticated_user: Перенаправление аутентифицированных пользователей.
    :type redirect_authenticated_user: bool
    :attribute success_url: URL для перенаправления после успешного входа.
    :type success_url: str
    """
    template_name: str = 'login.html'
    form_class: AuthenticationForm = AuthenticationForm
    redirect_authenticated_user: bool = True
    success_url: str = reverse_lazy('profile')

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        """
        Обрабатывает валидную форму и выполняет вход пользователя.

        :param form: Форма с данными аутентификации.
        :type form: :class:`django.contrib.auth.forms.AuthenticationForm`
        :returns: Результат обработки формы.
        :rtype: :class:`django.http.HttpResponse`
        """
        response: HttpResponse = super().form_valid(form)
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return response

    def form_invalid(self, form: AuthenticationForm) -> HttpResponse:
        """
        Обрабатывает случай, когда форма невалидна.

        :param form: Форма с невалидными данными.
        :type form: :class:`django.contrib.auth.forms.AuthenticationForm`
        :returns: Результат обработки невалидной формы.
        :rtype: :class:`django.http.HttpResponse`
        """
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)

class NotFoundView(TemplateView):
    """
    Представление для отображения страницы ошибки 404.

    :attribute template_name: Шаблон для страницы 404.
    :type template_name: str
    """
    template_name: str = '404.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет дополнительные данные в контекст шаблона.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с дополнительными данными.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        return context

class FieldDetailView(DetailView):
    """
    Представление для отображения деталей поля.

    :attribute model: Модель поля.
    :type model: :class:`main_app.models.Field`
    :attribute template_name: Шаблон для страницы деталей.
    :type template_name: str
    :attribute context_object_name: Имя объекта поля в контексте шаблона.
    :type context_object_name: str
    """
    model: Field = Field
    template_name: str = 'card_detail.html'
    context_object_name: str = 'field'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет дополнительные данные в контекст шаблона.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с дополнительными данными.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        field: Field = self.get_object()
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

    def get_object(self, queryset: Optional[QuerySet[Field]] = None) -> Field:
        """
        Возвращает объект поля.

        :param queryset: Набор данных для выборки объекта (не используется).
        :type queryset: Optional[:class:`django.db.models.QuerySet`[:class:`main_app.models.Field`]]
        :returns: Объект поля.
        :rtype: :class:`main_app.models.Field`
        :raises Http404: Если поле заблокировано.
        """
        obj: Field = super().get_object(queryset)
        if obj.is_blocked:
            raise Http404("Карта заблокирована и недоступна для просмотра")
        return obj

    def create_cells(self, field: Field) -> None:
        """
        Создает клетки для поля при первом обращении.

        :param field: Объект поля.
        :type field: :class:`main_app.models.Field`
        """
        cells: List[Cell] = []
        for x in range(field.cols):
            for y in range(field.rows):
                cells.append(Cell(field=field, x=x, y=y))
        Cell.objects.bulk_create(cells)

class ReportFieldView(LoginRequiredMixin, CreateView):
    """
    Представление для отправки жалобы на содержимое поля.

    Обрабатывает причину и описание жалобы, проверяет их на валидность
    и создает новый экземпляр FieldReport.

    :attribute model: Модель жалобы.
    :type model: :class:`main_app.models.FieldReport`
    :attribute form_class: Форма для жалобы.
    :type form_class: :class:`main_app.forms.FieldReportForm`
    :attribute template_name: Шаблон для страницы жалобы.
    :type template_name: str
    """
    model: FieldReport = FieldReport
    form_class: FieldReportForm = FieldReportForm
    template_name: str = 'report_field.html'

    def get_success_url(self) -> str:
        """
        Возвращает URL для перенаправления после успешной отправки жалобы.

        :returns: URL страницы поля.
        :rtype: str
        """
        return reverse_lazy('index')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет объект поля в контекст шаблона.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с полем и формой.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        field: Field = get_object_or_404(Field, id=self.kwargs['field_id'])
        context['field'] = field
        context['existing_report'] = FieldReport.objects.filter(
            field_id=field.id,
            user=self.request.user,
            is_resolved=False
        ).first()
        return context

    def form_valid(self, form: FieldReportForm) -> HttpResponse:
        """
        Обрабатывает валидную форму и создает жалобу.

        :param form: Заполненная форма жалобы.
        :type form: :class:`main_app.forms.FieldReportForm`
        :returns: Перенаправление на URL успешной отправки.
        :rtype: :class:`django.http.HttpResponse`
        :raises ValidationError: Если данные формы невалидны.
        """
        try:
            self.validate_report(form.cleaned_data)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)
        report: FieldReport = form.save(commit=False)
        report.field = get_object_or_404(Field, id=self.kwargs['field_id'])
        report.user = self.request.user
        report.save()
        messages.success(self.request, 'Жалоба успешно отправлена!')
        return super().form_valid(form)

    def validate_report(self, cleaned_data: Dict[str, Any]) -> None:
        """
        Проверяет данные жалобы на валидность.

        :param cleaned_data: Очищенные данные формы.
        :type cleaned_data: Dict[str, Any]
        :raises ValidationError: Если данные невалидны.
        """
        reason: Optional[str] = cleaned_data.get('reason')
        description: Optional[str] = cleaned_data.get('description')
        if not reason:
            raise ValidationError('Укажите причину жалобы.')
        if reason == 'other' and not description:
            raise ValidationError('Для причины "Другое" необходимо описание.')
        existing_report: bool = FieldReport.objects.filter(
            field_id=self.kwargs['field_id'],
            user=self.request.user,
            is_resolved=False
        ).exists()
        if existing_report:
            raise ValidationError('Вы уже отправляли жалобу на это поле.')

def search_fields(request: HttpRequest) -> JsonResponse:
    """
    Выполняет поиск полей по запросу.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :returns: JSON-ответ с результатами поиска.
    :rtype: :class:`django.http.JsonResponse`
    """
    query: str = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    fields: QuerySet[Field] = (Field.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
              .values('id', 'title', 'description', 'created_at'))
    results: List[Dict[str, Any]] = []
    for field in fields:
        field['created_at'] = field['created_at'].strftime('%d.%m.%Y')
        results.append(field)
    return JsonResponse({'results': results})

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Миксин для ограничения доступа только для сотрудников.

    :attribute login_url: URL для перенаправления неавторизованных пользователей.
    :type login_url: str
    :attribute raise_exception: Вызывать исключение при отсутствии доступа.
    :type raise_exception: bool
    """
    login_url: str = reverse_lazy('login')
    raise_exception: bool = True

    def test_func(self) -> bool:
        """
        Проверяет, является ли пользователь сотрудником.

        :returns: ``True``, если пользователь является сотрудником.
        :rtype: bool
        """
        return self.request.user.is_staff

class ModerationPanelView(StaffRequiredMixin, TemplateView):
    """
    Представление для панели модерации.

    :attribute template_name: Шаблон для панели модерации.
    :type template_name: str
    """
    template_name: str = 'moderation/panel.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет данные о жалобах и заблокированном контенте в контекст.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с данными для модерации.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
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
    """
    Представление для обработки жалоб на комментарии.
    """
    def get(self, request: HttpRequest, report_id: int) -> HttpResponse:
        """
        Отображает страницу обработки жалобы на комментарий.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param report_id: ID жалобы.
        :type report_id: int
        :returns: Страница обработки жалобы.
        :rtype: :class:`django.http.HttpResponse`
        """
        report: ReportComment = get_object_or_404(ReportComment, id=report_id)
        return render(request, 'moderation/resolve_comment.html', {
            'report': report,
        })

    def post(self, request: HttpRequest, report_id: int) -> HttpResponse:
        """
        Обрабатывает действие по жалобе на комментарий.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param report_id: ID жалобы.
        :type report_id: int
        :returns: Перенаправление на панель модерации.
        :rtype: :class:`django.http.HttpResponse`
        """
        report: ReportComment = get_object_or_404(ReportComment, id=report_id)
        action: Optional[str] = request.POST.get('action')
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
    """
    Представление для обработки жалоб на поля.
    """
    def get(self, request: HttpRequest, report_id: int) -> HttpResponse:
        """
        Отображает страницу обработки жалобы на поле.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param report_id: ID жалобы.
        :type report_id: int
        :returns: Страница обработки жалобы.
        :rtype: :class:`django.http.HttpResponse`
        """
        report: FieldReport = get_object_or_404(FieldReport, id=report_id)
        return render(request, 'moderation/resolve_field.html', {
            'report': report,
        })

    def post(self, request: HttpRequest, report_id: int) -> HttpResponse:
        """
        Обрабатывает действие по жалобе на поле.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param report_id: ID жалобы.
        :type report_id: int
        :returns: Перенаправление на панель модерации.
        :rtype: :class:`django.http.HttpResponse`
        """
        report: FieldReport = get_object_or_404(FieldReport, id=report_id)
        action: Optional[str] = request.POST.get('action')
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

class AboutPageView(TemplateView):
    """
    Представление для страницы "О нас".

    :attribute template_name: Шаблон для страницы "О нас".
    :type template_name: str
    """
    template_name: str = 'about.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет информацию о компании в контекст.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с данными о компании.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['company_name'] = "Моя Компания"
        context['foundation_year'] = "2010"
        context['team_size'] = "50"
        context['team_members'] = [
            {
                'name': 'Иван Иванов',
                'position': 'Основатель и CEO',
                'bio': 'Иван основал компанию в 2010 с видением создания '
                       'инновационных решений для бизнеса.',
                'image': 'team-member1.jpg'
            },
            {
                'name': 'Алексей Петров',
                'position': 'Технический директор',
                'bio': 'Алексей присоединился к команде в 2012 и '
                       'возглавляет техническое развитие компании.',
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
    """
    Представление для страницы "Цели".

    :attribute template_name: Шаблон для страницы целей.
    :type template_name: str
    """
    template_name: str = 'goals.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет данные о миссии и целях в контекст.

        :param kwargs: Дополнительные аргументы.
        :type kwargs: Any
        :returns: Контекст с данными о целях.
        :rtype: Dict[str, Any]
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['mission'] = ("Мы стремимся создавать инновационные решения, "
                              "которые делают бизнес эффективнее.")
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
def toggle_like(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Переключает состояние лайка для поля.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID поля.
    :type pk: int
    :returns: JSON-ответ с текущим состоянием лайка и количеством лайков.
    :rtype: :class:`django.http.JsonResponse`
    """
    field: Field = Field.objects.get(id=pk)
    if request.user in field.likes.all():
        field.likes.remove(request.user)
        is_liked: bool = False
    else:
        field.likes.add(request.user)
        is_liked: bool = True
    return JsonResponse({
        'is_liked': is_liked,
        'likes_count': field.likes.count()
    })

@require_POST
@login_required
def toggle_favorite(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Переключает состояние избранного для поля.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID поля.
    :type pk: int
    :returns: JSON-ответ с текущим состоянием избранного.
    :rtype: :class:`django.http.JsonResponse`
    """
    field: Field = Field.objects.get(id=pk)
    if request.user in field.favorites.all():
        field.favorites.remove(request.user)
        is_favorited: bool = False
    else:
        field.favorites.add(request.user)
        is_favorited: bool = True
    return JsonResponse({
        'is_favorited': is_favorited
    })

@require_POST
@login_required
def add_comment(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Добавляет комментарий к полю.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID поля.
    :type pk: int
    :returns: JSON-ответ с данными о новом комментарии или ошибкой.
    :rtype: :class:`django.http.JsonResponse`
    :raises json.JSONDecodeError: Если тело запроса содержит некорректный JSON.
    """
    try:
        data: Dict[str, Any] = json.loads(request.body)
        text: str = data.get('text', '').strip()
        if not text:
            return JsonResponse({'error': 'Comment text cannot be empty'}, status=400)
        if len(text) > 1000:
            return JsonResponse({'error': 'Comment is too long (max 1000 chars)'}, status=400)
        field: Field = get_object_or_404(Field, id=pk)
        comment: Comment = Comment.objects.create(
            field=field,
            author=request.user,
            text=text
        )
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'author': comment.author.username,
            'text': comment.text,
            'created_at': (comment.created_at.strftime("%Y-%m-%d %H:%M")
                           if comment.created_at else None)
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in add_comment: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

def field_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Отображает страницу деталей поля.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID поля.
    :type pk: int
    :returns: Страница с деталями поля.
    :rtype: :class:`django.http.HttpResponse`
    """
    field: Field = Field.objects.get(id=pk)
    is_liked: bool = request.user.is_authenticated and request.user in field.likes.all()
    is_favorited: bool = request.user.is_authenticated and request.user in field.favorites.all()
    return render(request, 'your_app/field_detail.html', {
        'field': field,
        'is_liked': is_liked,
        'is_favorited': is_favorited
    })

@staff_member_required
def moderation_panel(request: HttpRequest) -> HttpResponse:
    """
    Отображает панель модерации с жалобами.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :returns: Страница панели модерации.
    :rtype: :class:`django.http.HttpResponse`
    """
    reports: QuerySet[FieldReport] = FieldReport.objects.filter(status='pending').select_related('field', 'user')
    return render(request, 'moderation/moderation_panel.html', {
        'reports': reports
    })

@staff_member_required
def block_content(request: HttpRequest, content_type: str, content_id: int) -> HttpResponse:
    """
    Универсальная функция для блокировки контента.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param content_type: Тип контента (field, comment, user).
    :type content_type: str
    :param content_id: ID контента.
    :type content_id: int
    :returns: Перенаправление на панель администрирования.
    :rtype: :class:`django.http.HttpResponse`
    :raises Http404: Если тип контента не поддерживается.
    """
    content_types: Dict[str, Dict[str, Any]] = {
        'field': {
            'model': Field,
            'block_method': 'safe_block',
            'unblock_method': 'safe_unblock',
            'name': 'карта'
        },
        'comment': {
            'model': Comment,
            'block_method': 'safe_block',
            'unblock_method': 'safe_unblock',
            'name': 'комментарий'
        },
        'user': {
            'model': User,
            'block_method': 'safe_ban',
            'unblock_method': None,
            'name': 'пользователь'
        }
    }
    try:
        if content_type not in content_types:
            raise Http404("Тип контента не поддерживается")
        config: Dict[str, Any] = content_types[content_type]
        model: Any = config['model']
        item: Any = get_object_or_404(model, pk=content_id)
        action: str = request.POST.get('action', 'block')
        if action == 'block' and config['block_method']:
            method = getattr(item, config['block_method'])
            success_msg: str = f"{config['name'].capitalize()} успешно заблокирован"
            log_action: str = 'блокировка'
        elif action == 'unblock' and config['unblock_method']:
            method = getattr(item, config['unblock_method'])
            success_msg: str = f"{config['name'].capitalize()} разблокирован"
            log_action: str = 'разблокировка'
        else:
            messages.error(request, "Действие недоступно для этого типа контента")
            return redirect('admin-panel')

        if method():
            messages.success(request, success_msg)
            logger.info("%s %s %s", log_action.capitalize(), config['name'], content_id)
        else:
            messages.error(request, "Не удалось выполнить действие для %s", config['name'])
    except Exception as e:
        logger.error("Ошибка в block_content: %s", str(e), exc_info=True)
        messages.error(request, f"Произошла ошибка: {str(e)}")
    return redirect(reverse_lazy('admin-panel'))

class BlockContentView(View):
    """
    Класс для блокировки контента.
    """
    def post(self, request: HttpRequest, content_type: str, content_id: int) -> HttpResponse:
        """
        Обрабатывает запрос на блокировку контента.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param content_type: Тип контента (field, comment, user).
        :type content_type: str
        :param content_id: ID контента.
        :type content_id: int
        :returns: Перенаправление на панель модерации.
        :rtype: :class:`django.http.HttpResponse`
        :raises ValueError: Если тип контента неизвестен.
        """
        content_types: Dict[str, Dict[str, Any]] = {
            'field': {
                'model': Field,
                'block_method': 'safe_block',
                'name': 'карта',
                'detail_url': 'field_detail'
            },
            'comment': {
                'model': Comment,
                'block_method': 'safe_block',
                'name': 'комментарий',
                'detail_url': None
            },
            'user': {
                'model': User,
                'block_method': 'safe_ban',
                'name': 'пользователь',
                'detail_url': 'profile_view'
            }
        }
        try:
            if content_type not in content_types:
                raise ValueError("Неизвестный тип контента")
            config: Dict[str, Any] = content_types[content_type]
            item: Any = config['model'].objects.get(pk=content_id)
            if hasattr(item, config['block_method']):
                getattr(item, config['block_method'])()
                messages.success(request, f"{config['name'].capitalize()} успешно заблокирована")
                logger.info("Заблокирован %s %s", content_type, content_id)
            else:
                messages.error(request, "Не удалось заблокировать")
        except Exception as e:
            messages.error(request, "Ошибка: %s", str(e))
            logger.error("Ошибка блокировки: %s", str(e))
        return redirect(reverse('moderation_panel'))

class UnblockContentView(View):
    """
    Класс для разблокировки контента.
    """
    def post(self, request: HttpRequest, content_type: str, content_id: int) -> HttpResponse:
        """
        Обрабатывает запрос на разблокировку контента.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param content_type: Тип контента (field, comment).
        :type content_type: str
        :param content_id: ID контента.
        :type content_id: int
        :returns: Перенаправление на панель модерации.
        :rtype: :class:`django.http.HttpResponse`
        :raises ValueError: Если тип контента неизвестен.
        """
        content_types: Dict[str, Dict[str, Any]] = {
            'field': {
                'model': Field,
                'unblock_method': 'safe_unblock',
                'name': 'карта',
                'detail_url': 'field_detail'
            },
            'comment': {
                'model': Comment,
                'unblock_method': 'safe_unblock',
                'name': 'комментарий',
                'detail_url': None
            }
        }
        try:
            if content_type not in content_types:
                raise ValueError("Неизвестный тип контента")
            config: Dict[str, Any] = content_types[content_type]
            item: Any = config['model'].objects.get(pk=content_id)
            if hasattr(item, config['unblock_method']):
                getattr(item, config['unblock_method'])()
                messages.success(request, f"{config['name'].capitalize()} успешно разблокирована")
                logger.info("Разблокирован %s %s", content_type, content_id)
            else:
                messages.error(request, "Не удалось разблокировать")
        except Exception as e:
            messages.error(request, "Ошибка: %s", str(e))
            logger.error("Ошибка разблокировки: %s", str(e))
        return redirect(reverse('moderation_panel'))

class ProfileFieldsAPIView(View):
    """
    API-представление для получения полей пользователя.
    """
    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Возвращает список полей пользователя в зависимости от типа запроса.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :returns: JSON-ответ с данными о полях.
        :rtype: :class:`django.http.JsonResponse`
        """
        field_type: str = request.GET.get('type', 'my')
        if field_type == 'my':
            fields: QuerySet[Field] = Field.objects.filter(user=request.user)
        elif field_type == 'liked':
            fields: QuerySet[Field] = request.user.liked_cards.all()
        elif field_type == 'favorites':
            fields: QuerySet[Field] = request.user.favorited_cards.all()
        else:
            fields: QuerySet[Field] = Field.objects.none()
        fields_data: List[Dict[str, Any]] = []
        for field in fields:
            fields_data.append({
                'id': field.id,
                'title': field.title,
                'description': field.description,
                'created_at': field.created_at.strftime("%d.%m.%Y"),
                'url': field.get_absolute_url()
            })
        return JsonResponse({'fields': fields_data})

@require_POST
@login_required
def toggle_comment_like(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Переключает состояние лайка для комментария.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID комментария.
    :type pk: int
    :returns: JSON-ответ с текущим состоянием лайка и количеством лайков.
    :rtype: :class:`django.http.JsonResponse`
    """
    try:
        comment: Comment = Comment.objects.get(id=pk)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            is_liked: bool = False
        else:
            comment.likes.add(request.user)
            is_liked: bool = True
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': comment.likes.count()
        })
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Комментарий не найден'}, status=404)

@require_POST
@login_required
def report_comment(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Отправляет жалобу на комментарий.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID комментария.
    :type pk: int
    :returns: JSON-ответ с результатом отправки жалобы.
    :rtype: :class:`django.http.JsonResponse`
    """
    try:
        comment: Comment = Comment.objects.get(id=pk)
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
def add_wall(request: HttpRequest) -> JsonResponse:
    """
    Добавляет новую стену.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :returns: JSON-ответ с данными о новой стене или ошибкой.
    :rtype: :class:`django.http.JsonResponse`
    :raises json.JSONDecodeError: Если тело запроса содержит некорректный JSON.
    """
    try:
        data: Dict[str, Any] = json.loads(request.body)
        field_id: int = data.get('field_id')
        x: int = int(data.get('x'))
        y: int = int(data.get('y'))
        width: int = int(data.get('width', 1))
        height: int = int(data.get('height', 1))
        field: Field = Field.objects.get(id=field_id)
        if x + width > field.cols or y + height > field.rows:
            return JsonResponse({'error': 'Wall exceeds field boundaries'}, status=400)
        wall: Wall = Wall.objects.create(
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
def remove_wall(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Удаляет стену.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID стены.
    :type pk: int
    :returns: JSON-ответ с результатом удаления.
    :rtype: :class:`django.http.JsonResponse`
    """
    try:
        wall: Wall = Wall.objects.get(id=pk)
        if wall.created_by != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        wall.delete()
        return JsonResponse({'success': True})
    except Wall.DoesNotExist:
        return JsonResponse({'error': 'Wall not found'}, status=404)

def get_field_state(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Получает текущее состояние поля.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID поля.
    :type pk: int
    :returns: JSON-ответ с данными о состоянии поля.
    :rtype: :class:`django.http.JsonResponse`
    """
    try:
        field: Field = Field.objects.get(id=pk)
        walls: QuerySet[Wall] = Wall.objects.filter(field=field).values('id', 'x', 'y', 'width', 'height')
        return JsonResponse({
            'cols': field.cols,
            'rows': field.rows,
            'walls': list(walls)
        })
    except Field.DoesNotExist:
        return JsonResponse({'error': 'Field not found'}, status=404)

def custom_logout(request: HttpRequest) -> HttpResponse:
    """
    Выполняет выход пользователя из системы.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :returns: Перенаправление на страницу входа.
    :rtype: :class:`django.http.HttpResponse`
    """
    logout(request)
    return redirect('login')

class FieldCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового поля.

    :attribute model: Модель поля.
    :type model: :class:`main_app.models.Field`
    :attribute form_class: Форма для создания поля.
    :type form_class: :class:`main_app.forms.FieldForm`
    :attribute template_name: Шаблон для страницы создания.
    :type template_name: str
    :attribute success_url: URL для перенаправления после успешного создания.
    :type success_url: str
    """
    model: Field = Field
    form_class: FieldForm = FieldForm
    template_name: str = 'create_field.html'
    success_url: str = reverse_lazy('index')

    def form_valid(self, form: FieldForm) -> HttpResponse:
        """
        Обрабатывает валидную форму создания поля.

        :param form: Форма создания поля.
        :type form: :class:`main_app.forms.FieldForm`
        :returns: Результат обработки формы.
        :rtype: :class:`django.http.HttpResponse`
        """
        field: Field = form.save(commit=False)
        field.user = self.request.user
        file_data: Optional[Dict[str, Any]] = form.cleaned_data.get('file')
        if file_data:
            field_file: FieldFile = FieldFile.objects.create(
                name=file_data['name'],
                content_type=file_data['content_type'],
                data=file_data['data'],
                size=file_data['size']
            )
            field.file = field_file
        field.save()
        return super().form_valid(form)

def download_file(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Скачивает файл, связанный с полем.

    :param request: HTTP-запрос.
    :type request: :class:`django.http.HttpRequest`
    :param pk: ID файла.
    :type pk: int
    :returns: Ответ с файлом для скачивания.
    :rtype: :class:`django.http.HttpResponse`
    """
    field_file: FieldFile = get_object_or_404(FieldFile, pk=pk)
    response: HttpResponse = HttpResponse(field_file.data, content_type=field_file.content_type)
    response['Content-Disposition'] = f'attachment; filename="{field_file.name}"'
    return response