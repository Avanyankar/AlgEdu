"""
Тесты для сайта команды AlgEdu
"""
import logging
from unittest.mock import MagicMock, patch
from django.contrib.admin import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse, resolve
from main_app.admin import FieldReportAdmin
from main_app.views import (IndexView, UserLoginView, ProfileUpdateView, ProfileView, UserRegisterView, FieldDetailView,
                            ReportFieldView, AboutPageView, GoalsPageView, FieldCreateView, ModerationPanelView,
                            ProfileFieldsAPIView, ResolveFieldReportView, ResolveCommentReportView, UnblockContentView,
                            BlockContentView, moderation_panel, FieldListView)
from main_app.models import User, Field, Comment, ProfileComment, Wall, Cell, FieldReport
from main_app.forms import FieldForm, ProfileUpdateForm, RegistrationForm
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

    def test_template_used(self):
        """Проверяем использование правильного шаблона"""
        self.client.force_login(self.staff_user)
        response = self.client.get('/moderation/')
        self.assertTemplateUsed(response, 'moderation/panel.html')


class FieldListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.factory = RequestFactory()
        self.field1 = Field.objects.create(
            user=self.user,
            title='Field1',
            description='Test',
            cols=10,
            rows=10
        )
        self.field2 = Field.objects.create(
            user=self.user,
            title='Field2',
            description='Test',
            cols=10,
            rows=10
        )
        self.blockedField = Field.objects.create(
            user=self.user,
            title='BlockedField ',
            description='Test',
            cols=10,
            rows=10
        )
        self.blockedField.block()
        self.logger = logging.getLogger('django')
        self.handler = logging.StreamHandler()
        self.logger.addHandler(self.handler)
        self.handler.stream = self.captured_logs = []

    def test_class_attributes(self):
        """Проверка атрибутов класса"""
        self.assertEqual(FieldListView.model, Field)
        self.assertEqual(FieldListView.template_name, 'fields/list.html')
        self.assertEqual(FieldListView.context_object_name, 'fields')

    def test_block_field(self):
        """Проверка блокировки поля"""
        self.assertTrue(self.blockedField.is_blocked)

    def test_get_queryset_returns_unblocked_fields(self):
        """Тестирование возвращаемого QuerySet"""
        request = self.factory.get('/fields/')
        view = FieldListView()
        view.setup(request)
        queryset = view.get_queryset()
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(queryset.count(), 2)
        titles = sorted([queryset[0].title, queryset[1].title])
        self.assertEqual(titles[0], "Field1")
        self.assertEqual(titles[1], "Field2")


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


class UserRegisterViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('registration')
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        }

    def test_form_valid_success(self):
        """Тест успешной регистрации пользователя."""
        request = self.factory.post(self.url, data=self.valid_data)
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        with patch('main_app.views.user_registered.send') as mock_send, \
                patch('main_app.views.login') as mock_login, \
                patch('main_app.views.logger.info') as mock_logger:
            view = UserRegisterView.as_view()
            response = view(request)
            self.assertTrue(User.objects.filter(username='testuser').exists())
            mock_send.assert_called_once_with(
                sender=UserRegisterView,
                user=User.objects.get(username='testuser'),
                request=request
            )
            mock_login.assert_called_once_with(
                request,
                User.objects.get(username='testuser')
            )
            mock_logger.assert_called_once_with(
                "Successful registration of a new user: %s", 'testuser'
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('login'))

    def test_form_valid_error(self):
        """Тест обработки ошибки при регистрации."""
        request = self.factory.post(self.url, data=self.valid_data)
        with patch('main_app.views.RegistrationForm.save', side_effect=Exception("Test error")), \
                patch('main_app.views.logger.error') as mock_logger:
            view = UserRegisterView.as_view()
            with self.assertRaises(Exception):
                view(request)
            mock_logger.assert_called_once_with(
                "Error during user registration: %s", "Test error", exc_info=True
            )

    def test_register_method(self):
        """Тест метода register()."""
        request = self.factory.post(self.url, data=self.valid_data)
        mock_form = MagicMock(spec=RegistrationForm)
        mock_user = MagicMock()
        mock_form.save.return_value = mock_user
        view = UserRegisterView()
        view.request = request
        with patch('main_app.views.user_registered.send') as mock_send:
            result = view.register(mock_form)
            mock_form.save.assert_called_once()
            mock_send.assert_called_once_with(
                sender=UserRegisterView,
                user=mock_user,
                request=request
            )
            self.assertEqual(result, mock_user)


class FieldReportAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = FieldReportAdmin(FieldReport, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='admin',
            password='password',
            email='admin@example.com'
        )
        self.field = Field.objects.create(
            user=self.user,
            title='Test Field',
            description='Test',
            cols=10,
            rows=10
        )
        self.pending_report = FieldReport.objects.create(
            field=self.field,
            user=self.user,
            reason='spam',
            status='pending'
        )
        self.resolved_report = FieldReport.objects.create(
            field=self.field,
            user=self.user,
            reason='spam',
            status='resolved'
        )

    def test_moderate_reports_get(self):
        """Тест GET-запроса: отображение панели модерации."""
        request = self.factory.get('/admin/fieldreport/moderation-panel/')
        request.user = self.user
        response = self.admin.moderate_reports(request)
        self.assertEqual(response.status_code, 200)

    def test_moderate_reports_post_valid(self):
        """Тест POST-запроса с валидными данными."""
        request = self.factory.post('/admin/fieldreport/moderation-panel/', {
            'report_id': str(self.pending_report.id),
            'action': 'approve'
        })
        request.user = self.user
        with patch.object(self.admin, 'change_report_status') as mock_change:
            mock_change.return_value = HttpResponseRedirect('/redirect/')
            response = self.admin.moderate_reports(request)
            mock_change.assert_called_once_with(request, str(self.pending_report.id), 'approve')
            self.assertEqual(response.status_code, 302)

    def test_moderate_reports_post_invalid(self):
        """Тест POST-запроса с невалидными данными."""
        request = self.factory.post('/admin/fieldreport/moderation-panel/', {
            'report_id': '',
            'action': ''
        })
        request.user = self.user
        response = self.admin.moderate_reports(request)
        self.assertEqual(response.status_code, 200)
