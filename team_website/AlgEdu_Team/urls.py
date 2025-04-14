"""
URL configuration for AlgEdu_Team project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import main_app.views as views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.IndexView.as_view() , name='index'),
    path('profile_update/', views.ProfileUpdateView.as_view() , name='profile_update'),
    path('registration/', views.UserRegisterView.as_view() , name='registration'),
    path('accounts/login/', views.UserLoginView.as_view() , name='login'),
    path('cards/<int:pk>/', views.FieldDetailView.as_view(), name='card-detail'),
    path('cards/<int:pk>/toggle-like/', views.toggle_like, name='toggle-like'),
    path('cards/<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('api/search/', views.search_fields, name='search_api'),
    path('cards/<int:field_id>/report/', views.ReportFieldView.as_view(), name='report_field'),
    path('cards/<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('comments/<int:pk>/toggle-like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('comments/<int:pk>/report/', views.report_comment, name='report_comment'),
    path('field/<int:pk>/', views.FieldDetailView.as_view(), name='field_detail'),
    path('api/field/<int:pk>/toggle-like/', views.toggle_like, name='toggle_like'),
    path('api/field/<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('api/field/<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('api/comment/<int:pk>/toggle-like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('api/comment/<int:pk>/report/', views.report_comment, name='report_comment'),
    path('api/field/<int:pk>/state/', views.get_field_state, name='field_state'),
    path('api/walls/add/', views.add_wall, name='add_wall'),
    path('api/walls/<int:pk>/remove/', views.remove_wall, name='remove_wall'),
    path('api/search/', views.search_fields, name='search_fields'),
    path('spinning/', views.spinning_image_view, name='spinning_image'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.custom_logout, name='logout'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('goals/', views.GoalsPageView.as_view(), name='goals'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile_view'),
    path('profile/<str:username>/comment/', views.add_profile_comment, name='add_profile_comment'),
    path('profile/comment/<int:comment_id>/delete/', views.delete_profile_comment, name='delete_profile_comment'),
    path('fields/create/', views.FieldCreateView.as_view(), name='create_field'),
    path('files/download/<int:pk>/', views.download_file, name='download_file'),
    path('moderation/', views.ModerationPanelView.as_view(), name='moderation_panel'),
    path('moderation/field/<int:report_id>/', views.ResolveFieldReportView.as_view(), name='resolve_field_report'),
    path('moderation/comment/<int:report_id>/', views.ResolveCommentReportView.as_view(), name='resolve_comment_report'),
    path('moderation/unblock/<str:content_type>/<int:content_id>/', views.UnblockContentView.as_view(), name='unblock_content'),
    path('api/profile/fields/', views.ProfileFieldsAPIView.as_view(), name='profile_fields_api'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.NotFoundView.as_view()