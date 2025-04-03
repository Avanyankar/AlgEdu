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
from django.urls import path
import main_app.views as views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', views.ProfileView.as_view() , name='profile'),
    path('', views.IndexView.as_view() , name='index'),
    path('profile_update/', views.ProfileUpdateView.as_view() , name='profile_update'),
    path('registration/', views.UserRegisterView.as_view() , name='registration'),
    path('login/', views.UserLoginView.as_view() , name='login'),
    path('cards/<int:pk>/', views.FieldDetailView.as_view(), name='card-detail'),
    path('cards/<int:pk>/toggle-like/', views.toggle_like, name='toggle-like'),
    path('cards/<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('api/search/', views.search_fields, name='search_api'),
    path('cards/<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('comments/<int:pk>/toggle-like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('comments/<int:pk>/report/', views.report_comment, name='report_comment'),
    path('field/<int:pk>/', views.FieldDetailView.as_view(), name='field_detail'),

    # API для взаимодействия
    path('api/field/<int:pk>/toggle-like/', views.toggle_like, name='toggle_like'),
    path('api/field/<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('api/field/<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('api/comment/<int:pk>/toggle-like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('api/comment/<int:pk>/report/', views.report_comment, name='report_comment'),

    # API для игрового поля
    path('api/field/<int:pk>/state/', views.get_field_state, name='field_state'),
    path('api/walls/add/', views.add_wall, name='add_wall'),
    path('api/walls/<int:pk>/remove/', views.remove_wall, name='remove_wall'),

    # Поиск
    path('api/search/', views.search_fields, name='search_fields'),
]

handler404 = views.NotFoundView.as_view()