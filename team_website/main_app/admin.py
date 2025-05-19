"""
Настройки административного интерфейса Django для моделей приложения.

Этот модуль определяет настройки админ-панели для моделей :class:`main_app.models.Field`
и :class:`main_app.models.FieldReport`, включая отображение списков, фильтры,
поиск, действия и пользовательские URL для модерации.

:mod:`main_app.admin`
"""

from typing import Any, List
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse
from .models import FieldReport, Field

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    """
    Класс админ-панели для модели :class:`main_app.models.Field`.

    :attribute list_display: Поля, отображаемые в списке.
    :type list_display: tuple[str, ...]
    :attribute list_filter: Поля для фильтрации списка.
    :type list_filter: tuple[str, ...]
    :attribute search_fields: Поля для поиска.
    :type search_fields: tuple[str, ...]
    :attribute filter_horizontal: Поля с горизонтальным выбором для ManyToMany.
    :type filter_horizontal: tuple[str, ...]
    """
    list_display: tuple[str, ...] = ('title', 'user', 'created_at')
    list_filter: tuple[str, ...] = ('created_at', 'user')
    search_fields: tuple[str, ...] = ('title', 'description')
    filter_horizontal: tuple[str, ...] = ('likes', 'favorites')

class FieldReportAdmin(admin.ModelAdmin):
    """
    Класс админ-панели для модели :class:`main_app.models.FieldReport`.

    :attribute list_display: Поля, отображаемые в списке.
    :type list_display: tuple[str, ...]
    :attribute list_filter: Поля для фильтрации списка.
    :type list_filter: tuple[str, ...]
    :attribute list_editable: Поля, редактируемые в списке.
    :type list_editable: tuple[str, ...]
    :attribute search_fields: Поля для поиска.
    :type search_fields: tuple[str, ...]
    :attribute actions: Действия, доступные для выбранных объектов.
    :type actions: list[str]
    :attribute ordering: Сортировка списка.
    :type ordering: tuple[str, ...]
    """
    list_display: tuple[str, ...] = ('field', 'user', 'reason', 'status', 'created_at', 'is_resolved')
    list_filter: tuple[str, ...] = ('status', 'reason', 'is_resolved')
    list_editable: tuple[str, ...] = ('status', 'is_resolved')
    search_fields: tuple[str, ...] = ('field__title', 'user__username', 'description')
    actions: list[str] = ['approve_selected_reports', 'reject_selected_reports']
    ordering: tuple[str, ...] = ('-created_at',)

    def get_urls(self) -> List[Any]:
        """
        Добавляет пользовательские URL для панели модерации жалоб.

        :returns: Список URL-адресов админ-панели.
        :rtype: List[Any]
        """
        urls: List[Any] = super().get_urls()
        custom_urls: List[Any] = [
            path(
                'moderation-panel/',
                self.admin_site.admin_view(self.moderate_reports),
                name='fieldreport_moderation_panel'
            ),
            path(
                'moderation-panel/<int:report_id>/change-status/',
                self.admin_site.admin_view(self.change_report_status),
                name='fieldreport_change_status'
            ),
        ]
        return custom_urls + urls

    def moderate_reports(self, request: Any) -> HttpResponse:
        """
        Отображает панель модерации жалоб и обрабатывает действия с жалобами.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :returns: Страница панели модерации или перенаправление.
        :rtype: :class:`django.http.HttpResponse`
        """
        if request.method == 'POST':
            report_id: str = request.POST.get('report_id')
            action: str = request.POST.get('action')
            if report_id and action:
                return self.change_report_status(request, report_id, action)
        reports: Any = FieldReport.objects.filter(status='pending').select_related('field', 'user')
        context: dict[str, Any] = {
            'reports': reports,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'title': 'Панель модерации жалоб',
        }
        return render(request, 'moderation/moderation_panel.html', context)

    def change_report_status(self, request: Any, report_id: int, action: str = None) -> HttpResponse:
        """
        Изменяет статус жалобы (одобрение или отклонение).

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param report_id: ID жалобы.
        :type report_id: int
        :param action: Действие (approve или reject).
        :type action: str, optional
        :returns: Перенаправление на панель модерации.
        :rtype: :class:`django.http.HttpResponse`
        :raises FieldReport.DoesNotExist: Если жалоба не найдена.
        """
        if not action:
            action = request.GET.get('action')
        try:
            report: FieldReport = FieldReport.objects.get(id=report_id)
            if action == 'approve':
                report.status = 'approved'
                report.is_resolved = True
                messages.success(request, f'Жалоба #{report_id} одобрена')
            elif action == 'reject':
                report.status = 'rejected'
                report.is_resolved = True
                messages.success(request, f'Жалоба #{report_id} отклонена')
            report.save()
        except FieldReport.DoesNotExist:
            messages.error(request, f'Жалоба #{report_id} не найдена')
        return redirect('moderation:fieldreport_moderation_panel')

    def approve_selected_reports(self, request: Any, queryset: Any) -> None:
        """
        Одобряет выбранные жалобы.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param queryset: Набор выбранных жалоб.
        :type queryset: :class:`django.db.models.QuerySet`[:class:`main_app.models.FieldReport`]
        """
        updated: int = queryset.update(status='approved', is_resolved=True)
        self.message_user(request, f'{updated} жалоб одобрено', messages.SUCCESS)

    approve_selected_reports.short_description = "Одобрить выбранные жалобы"

    def reject_selected_reports(self, request: Any, queryset: Any) -> None:
        """
        Отклоняет выбранные жалобы.

        :param request: HTTP-запрос.
        :type request: :class:`django.http.HttpRequest`
        :param queryset: Набор выбранных жалоб.
        :type queryset: :class:`django.db.models.QuerySet`[:class:`main_app.models.FieldReport`]
        """
        updated: int = queryset.update(status='rejected', is_resolved=True)
        self.message_user(request, f'{updated} жалоб отклонено', messages.SUCCESS)

    reject_selected_reports.short_description = "Отклонить выбранные жалобы"

admin.site.register(FieldReport, FieldReportAdmin)
