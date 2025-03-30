from django.contrib import admin
from django.contrib import admin
from .models import Field  # Импортируй свою модель


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'description')
    filter_horizontal = ('likes', 'favorites')
