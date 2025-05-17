from django.test import TestCase
from django.contrib.auth import get_user_model
from main_app.models import Field, Comment, ProfileComment, FieldReport

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)


class FieldModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_field_creation(self):
        field = Field.objects.create(
            user=self.user,
            title='Test Field',
            description='Test Description'
        )
        self.assertEqual(field.title, 'Test Field')
        self.assertEqual(field.user.username, 'testuser')
        self.assertFalse(field.is_blocked)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.field = Field.objects.create(
            user=self.user,
            title='Test Field',
            description='Test Description'
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            field=self.field,
            author=self.user,
            text='Test comment'
        )
        self.assertEqual(comment.text, 'Test comment')
        self.assertEqual(comment.author.username, 'testuser')
        self.assertFalse(comment.is_blocked)


class ProfileCommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_profile_comment_creation(self):
        comment = ProfileComment.objects.create(
            profile=self.user,
            author=self.user,
            text='Test profile comment'
        )
        self.assertEqual(comment.text, 'Test profile comment')
        self.assertEqual(comment.author.username, 'testuser')


class FieldReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.field = Field.objects.create(
            user=self.user,
            title='Test Field',
            description='Test Description'
        )

    def test_field_report_creation(self):
        report = FieldReport.objects.create(
            field=self.field,
            user=self.user,
            reason='spam'
        )
        self.assertEqual(report.reason, 'spam')
        self.assertEqual(report.status, 'pending')
        self.assertFalse(report.is_resolved)
from django.test import TestCase
from main_app.forms import RegistrationForm, ProfileUpdateForm, FieldForm

class RegistrationFormTest(TestCase):
    def test_valid_registration_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

class ProfileUpdateFormTest(TestCase):
    def test_valid_profile_update_form(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com'
        }
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

class FieldFormTest(TestCase):
    def test_valid_field_form(self):
        form_data = {
            'title': 'Test Field',
            'description': 'Test Description',
            'cols': 10,
            'rows': 10
        }
        form = FieldForm(data=form_data)
        self.assertTrue(form.is_valid())


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


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

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_successful_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect