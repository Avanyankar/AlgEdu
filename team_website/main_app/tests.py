from django.test import TestCase
from django.contrib.auth import get_user_model
from main_app.models import Field, Comment, ProfileComment, FieldReport, Wall, Cell

User = get_user_model()

from django.test import TestCase
from django.urls import reverse, resolve
from main_app.views import (
    IndexView, UserLoginView, UserRegisterView,
    ProfileView, ProfileUpdateView, FieldListView
)

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from main_app.views import StaffRequiredMixin

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from main_app.mixins import StaffRequiredMixin  # Предполагается, что миксин вынесен в отдельный файл

from django.test import TestCase
from django.contrib.auth.models import User
from main_app.mixins import StaffRequiredMixin
from django.views.generic import View


class StaffTestView(StaffRequiredMixin, View):
    pass


class StaffRequiredMixinTests(TestCase):
    def setUp(self):
        self.normal_user = User.objects.create_user(username='normal', password='test123')
        self.staff_user = User.objects.create_user(username='staff', password='test123', is_staff=True)

    def test_staff_user_access(self):
        view = StaffTestView()
        view.request = type('Request', (), {'user': self.staff_user})
        self.assertTrue(view.test_func())

    def test_normal_user_access(self):
        view = StaffTestView()
        view.request = type('Request', (), {'user': self.normal_user})
        self.assertFalse(view.test_func())

from django.test import TestCase
from django.urls import reverse, resolve
from main_app.views import IndexView, UserLoginView, ProfileView, ProfileUpdateView


class UrlTests(TestCase):
    def test_index_url(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func.view_class, IndexView)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, UserLoginView)

    def test_profile_url(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func.view_class, ProfileView)

    def test_profile_update_url(self):
        url = reverse('profile_update')
        self.assertEqual(resolve(url).func.view_class, ProfileUpdateView)

    # Удален тест для field_list, так как такого URL нет
class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.field = Field.objects.create(user=self.user, title='Test Field', description='Test', cols=10, rows=10)

    # 1-5
    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)

    def test_field_creation(self):
        self.assertEqual(Field.objects.count(), 1)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_field_str(self):
        self.assertEqual(str(self.field), 'Test Field')

    def test_comment_creation(self):
        comment = Comment.objects.create(field=self.field, author=self.user, text='Test')
        self.assertEqual(Comment.objects.count(), 1)

    # 6-10
    def test_profile_comment_creation(self):
        comment = ProfileComment.objects.create(profile=self.user, author=self.user, text='Test')
        self.assertEqual(ProfileComment.objects.count(), 1)

    def test_field_report_creation(self):
        report = FieldReport.objects.create(field=self.field, user=self.user, reason='spam')
        self.assertEqual(FieldReport.objects.count(), 1)

    def test_wall_creation(self):
        wall = Wall.objects.create(field=self.field, x=1, y=1, created_by=self.user)
        self.assertEqual(Wall.objects.count(), 1)

    def test_cell_creation(self):
        cell = Cell.objects.create(field=self.field, x=1, y=1)
        self.assertEqual(Cell.objects.count(), 1)

    def test_default_field_blocked_status(self):
        self.assertFalse(self.field.is_blocked)

    def test_field_likes(self):
        self.field.likes.add(self.user)
        self.assertEqual(self.field.likes.count(), 1)

    def test_field_favorites(self):
        self.field.favorites.add(self.user)
        self.assertEqual(self.field.favorites.count(), 1)

    def test_comment_likes(self):
        comment = Comment.objects.create(field=self.field, author=self.user, text='Test')
        comment.likes.add(self.user)
        self.assertEqual(comment.likes.count(), 1)

    def test_cell_default_blocked(self):
        cell = Cell.objects.create(field=self.field, x=1, y=1)
        self.assertFalse(cell.is_blocked)

    def test_wall_default_dimensions(self):
        wall = Wall.objects.create(field=self.field, x=1, y=1, created_by=self.user)
        self.assertEqual(wall.width, 1)
        self.assertEqual(wall.height, 1)


from django.test import TestCase
from main_app.forms import RegistrationForm, ProfileUpdateForm, FieldForm, CommentForm, FieldReportForm

def test_field_form_invalid_size(self):
    form_data = {
        'title': 'Test',
        'description': 'Test',
        'cols': 0,  # 0 должно быть недопустимым значением
        'rows': 0   # 0 должно быть недопустимым значением
    }
    form = FieldForm(data=form_data)
    self.assertFalse(form.is_valid())
    self.assertIn('cols', form.errors)
    self.assertIn('rows', form.errors)

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    # 16-20
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_goals_view(self):
        response = self.client.get(reverse('goals'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthorized(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    # 21-25
    def test_profile_view_authorized(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_field_create_view_unauthorized(self):
        response = self.client.get(reverse('create_field'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_successful_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после входа

    def test_logout(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Редирект после выхода

    def test_not_found_view(self):
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 200)

    def test_field_detail_view(self):
        field = Field.objects.create(
            user=self.user,
            title='Test Field',
            description='Test',
            cols=10,
            rows=10
        )
        response = self.client.get(reverse('field_detail', args=[field.id]))
        self.assertEqual(response.status_code, 200)

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    # 26-30
    def test_login_template(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')

    def test_index_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_about_template(self):
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'about.html')

    def test_goals_template(self):
        response = self.client.get(reverse('goals'))
        self.assertTemplateUsed(response, 'goals.html')

    def test_profile_template(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertTemplateUsed(response, 'profile.html')