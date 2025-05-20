"""
Тесты для сайта команды AlgEdu
"""
from django.core.exceptions import ValidationError
from django.test import TestCase, Client, SimpleTestCase, RequestFactory
from django.urls import reverse, resolve
from main_app.views import (IndexView, UserLoginView, ProfileUpdateView, ProfileView, UserRegisterView, FieldDetailView,
                            ReportFieldView, AboutPageView, GoalsPageView, FieldCreateView, ModerationPanelView,
                            ProfileFieldsAPIView, ResolveFieldReportView, ResolveCommentReportView, UnblockContentView,
                            BlockContentView, moderation_panel)
from main_app.models import User, Field, Comment, ProfileComment, FieldReport, Wall, Cell, FieldReport
from main_app.forms import FieldForm, ProfileUpdateForm
from django.contrib.auth.password_validation import validate_password
from django import forms
from django.utils.translation import gettext_lazy


class TemplateTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_index_content(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Карты не найдены')

    def test_about_template(self):
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'about.html')

    def test_about_content(self):
        response = self.client.get(reverse('about'))
        self.assertContains(response, 'Наша команда')


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Testpass1234!')

    def test_project_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')

    def test_password_validators(self):
        weak_passwords = [
            '1234',
            'password',
            'testuser',
            'abcdefgh',
            '12345678',
        ]
        for password in weak_passwords:
            with self.assertRaises(ValidationError):
                validate_password(password, user=self.user)
        try:
            validate_password('StrongPass123!', user=self.user)
        except ValidationError:
            self.fail("Сильный пароль не должен вызывать ValidationError")


class UrlTests(TestCase):
    def test_index_url(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func.view_class, IndexView)

    def test_profile_update_url(self):
        url = reverse('profile_update')
        self.assertEqual(resolve(url).func.view_class, ProfileUpdateView)

    def test_registration_url(self):
        url = reverse('registration')
        self.assertEqual(resolve(url).func.view_class, UserRegisterView)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, UserLoginView)

    def test_card_detail_url(self):
        url = reverse('card-detail', args=[1])
        self.assertEqual(resolve(url).func.view_class, FieldDetailView)

    def test_report_field_url(self):
        url = reverse('report_field', args=[1])
        self.assertEqual(resolve(url).func.view_class, ReportFieldView)

    def test_field_detail_url(self):
        url = reverse('field_detail', args=[1])
        self.assertEqual(resolve(url).func.view_class, FieldDetailView)

    def test_about_url(self):
        url = reverse('about')
        self.assertEqual(resolve(url).func.view_class, AboutPageView)

    def test_goals_url(self):
        url = reverse('goals')
        self.assertEqual(resolve(url).func.view_class, GoalsPageView)

    def test_profile_url(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func.view_class, ProfileView)

    def test_create_field_url(self):
        url = reverse('create_field')
        self.assertEqual(resolve(url).func.view_class, FieldCreateView)

    def test_moderation_panel_url(self):
        url = reverse('moderation_panel')
        self.assertEqual(resolve(url).func.view_class, ModerationPanelView)

    def test_profile_fields_api_url(self):
        url = reverse('profile_fields_api')
        self.assertEqual(resolve(url).func.view_class, ProfileFieldsAPIView)

    def test_resolve_field_report_url(self):
        url = reverse('resolve_field_report', args=[1])
        self.assertEqual(resolve(url).func.view_class, ResolveFieldReportView)

    def test_resolve_comment_report_url(self):
        url = reverse('resolve_comment_report', args=[1])
        self.assertEqual(resolve(url).func.view_class, ResolveCommentReportView)

    def test_unblock_content_url(self):
        url = reverse('unblock_content', args=['field', 1])
        self.assertEqual(resolve(url).func.view_class, UnblockContentView)

    def test_block_content_url(self):
        url = reverse('block_content', args=['field', 1])
        self.assertEqual(resolve(url).func.view_class, BlockContentView)


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.field = Field.objects.create(user=self.user, title='Test Field', description='Test', cols=10, rows=10)

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

    def test_profile_comment_str(self):
        comment = ProfileComment.objects.create(profile=self.user, author=self.user, text='Test')
        self.assertEqual(str(comment), "Комментарий от testuser к профилю testuser")

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

    def test_field_form_invalid_size(self):
        form_data = {
            'title': 'Test',
            'description': 'Test',
            'cols': -1,
            'rows': -1
        }
        form = FieldForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cols', form.errors)
        self.assertIn('rows', form.errors)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

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

    def test_profile_view_authorized(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_field_create_view_unauthorized(self):
        response = self.client.get(reverse('create_field'))
        self.assertEqual(response.status_code, 302)

    def test_successful_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

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


class PageTests(TestCase):
    def test_index_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_status_code(self):
        response = self.client.get('about/')
        self.assertEqual(response.status_code, 200)

    def test_goals_status_code(self):
        response = self.client.get('goals/')
        self.assertEqual(response.status_code, 200)


class ModerationPanelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.factory = RequestFactory()
        self.staff_user = User.objects.create_user(username='staff', is_staff=True)
        self.regular_user = User.objects.create_user(username='regular')
        self.field = Field.objects.create(
            user=self.user,
            title='Test Field',
            description='Test',
            cols=10,
            rows=10
        )
        self.report1 = FieldReport.objects.create(
            status='pending',
            user=self.regular_user,
            field=self.field
        )
        self.report2 = FieldReport.objects.create(
            status='approved',
            user=self.regular_user,
            field=self.field
        )

    def test_staff_access(self):
        request = self.factory.get('/moderation/')
        request.user = self.staff_user
        response = moderation_panel(request)
        self.assertEqual(response.status_code, 200)

    def test_regular_user_denied(self):
        """Проверяем, что обычный пользователь получает 302"""
        request = self.factory.get('/moderation/')
        request.user = self.regular_user
        response = moderation_panel(request)
        self.assertEqual(response.status_code, 302)

    def test_only_pending_reports_shown(self):
        """Проверяем, что отображаются только жалобы со статусом pending"""
        response = self.client.get('/moderation/')
        self.assertIn('reports', response.context)
        reports = response.context['reports']
        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first().id, self.report1.id)

    def test_template_used(self):
        """Проверяем использование правильного шаблона"""
        self.client.force_login(self.staff_user)
        response = self.client.get('/moderation/')
        self.assertTemplateUsed(response, 'moderation/panel.html')


class ProfileUpdateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.valid_data = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'new@example.com',
            'location': 'Москва',
            'birth_date': '1990-01-01',
            'bio': 'Тестовое описание'
        }

    def test_form_meta(self):
        """Проверка мета-данных формы"""
        form = ProfileUpdateForm()
        self.assertEqual(form._meta.model, User)
        expected_fields = ['first_name', 'last_name', 'email', 'location', 'birth_date', 'bio']
        self.assertEqual(form._meta.fields, expected_fields)
        self.assertIsInstance(form.fields['birth_date'].widget, forms.DateInput)
        self.assertIsInstance(form.fields['bio'].widget, forms.Textarea)
        self.assertEqual(form.fields['first_name'].label, gettext_lazy('Имя'))
        self.assertEqual(form.fields['last_name'].label, gettext_lazy('Фамилия'))
        self.assertEqual(form.fields['email'].label, gettext_lazy('Email'))
        self.assertEqual(form.fields['location'].label, gettext_lazy('Местоположение'))
        self.assertEqual(form.fields['birth_date'].label, gettext_lazy('Дата рождения'))
        self.assertEqual(form.fields['bio'].label, gettext_lazy('О себе'))

    def test_form_valid(self):
        """Проверка валидной формы"""
        form = ProfileUpdateForm(data=self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_email_unique_validation(self):
        """Проверка уникальности email"""
        User.objects.create_user(username='other', email='existing@example.com')
        form = ProfileUpdateForm(data={
            **self.valid_data,
            'email': 'test@example.com'
        }, instance=self.user)
        self.assertTrue(form.is_valid())
        form = ProfileUpdateForm(data={
            **self.valid_data,
            'email': 'existing@example.com'
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [gettext_lazy('Этот email уже используется')])

    def test_birth_date_validation(self):
        """Проверка валидации даты рождения"""
        form = ProfileUpdateForm(data={
            **self.valid_data,
            'birth_date': '1899-12-31'
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['birth_date'], [gettext_lazy('Некорректная дата рождения')])
        form = ProfileUpdateForm(data={
            **self.valid_data,
            'birth_date': '1900-01-01'
        }, instance=self.user)
        self.assertTrue(form.is_valid())
        form = ProfileUpdateForm(data={
            **self.valid_data,
            'birth_date': ''
        }, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Проверка сохранения формы"""
        form = ProfileUpdateForm(data=self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.last_name, 'Петров')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.location, 'Москва')
        self.assertEqual(str(user.birth_date), '1990-01-01')
        self.assertEqual(user.bio, 'Тестовое описание')