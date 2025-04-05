from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import FieldReport, Field, Comment, User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'description')
    filter_horizontal = ('likes', 'favorites')


class FieldReportAdmin(admin.ModelAdmin):
    list_display = ('field', 'user', 'reason', 'status', 'created_at', 'is_resolved')
    list_filter = ('status', 'reason', 'is_resolved')
    list_editable = ('status', 'is_resolved')
    search_fields = ('field__title', 'user__username', 'description')
    actions = ['approve_selected_reports', 'reject_selected_reports']
    ordering = ('-created_at',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
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
    
    def moderate_reports(self, request):
        if request.method == 'POST':
            report_id = request.POST.get('report_id')
            action = request.POST.get('action')
            if report_id and action:
                return self.change_report_status(request, report_id, action)
        
        reports = FieldReport.objects.filter(status='pending').select_related('field', 'user')
        context = {
            'reports': reports,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'title': 'Панель модерации жалоб',
        }
        return render(request, 'moderation/moderation_panel.html', context)
    
    def change_report_status(self, request, report_id, action=None):
        if not action:
            action = request.GET.get('action')
        
        try:
            report = FieldReport.objects.get(id=report_id)
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
    
    def approve_selected_reports(self, request, queryset):
        updated = queryset.update(status='approved', is_resolved=True)
        self.message_user(request, f'{updated} жалоб одобрено', messages.SUCCESS)
    approve_selected_reports.short_description = "Одобрить выбранные жалобы"
    
    def reject_selected_reports(self, request, queryset):
        updated = queryset.update(status='rejected', is_resolved=True)
        self.message_user(request, f'{updated} жалоб отклонено', messages.SUCCESS)
    reject_selected_reports.short_description = "Отклонить выбранные жалобы"

admin.site.register(FieldReport, FieldReportAdmin)