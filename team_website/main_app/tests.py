from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import Field, FieldFile
from .forms import FieldForm, DBFileField
from .views import FieldCreateView, download_file


class FieldModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.field_file = FieldFile.objects.create(
            name='test.txt',
            content_type='text/plain',
            data=b'Test content',
            size=12
        )
        self.field = Field.objects.create(
            user=self.user,
            title='Test Field',
            description='Test Description',
            cols=10,
            rows=10,
            file=self.field_file
        )

    def test_field_creation(self):
        self.assertEqual(self.field.title, 'Test Field')
        self.assertEqual(self.field.description, 'Test Description')
        self.assertEqual(self.field.cols, 10)
        self.assertEqual(self.field.rows, 10)
        self.assertEqual(self.field.file.name, 'test.txt')
        self.assertEqual(self.field.user.username, 'testuser')

    def test_field_file_creation(self):
        self.assertEqual(self.field_file.name, 'test.txt')
        self.assertEqual(self.field_file.content_type, 'text/plain')
        self.assertEqual(self.field_file.data, b'Test content')
        self.assertEqual(self.field_file.size, 12)

    def test_field_str(self):
        self.assertEqual(str(self.field), 'Test Field')

    def test_field_file_to_file(self):
        content_file = self.field_file.to_file()
        self.assertEqual(content_file.name, 'test.txt')
        self.assertEqual(content_file.read(), b'Test content')


class FieldFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'title': 'Test Field',
            'description': 'Test Description',
            'cols': 5,
            'rows': 5
        }
        form = FieldForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_title(self):
        form_data = {
            'description': 'Test Description',
            'cols': 5,
            'rows': 5
        }
        form = FieldForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_file_field_conversion(self):
        test_file = SimpleUploadedFile(
            "test.txt",
            b"Test file content",
            content_type="text/plain"
        )
        field = DBFileField()
        converted = field.to_python(test_file)

        self.assertEqual(converted['name'], 'test.txt')
        self.assertEqual(converted['content_type'], 'text/plain')
        self.assertEqual(converted['data'], b'Test file content')
        self.assertEqual(converted['size'], 16)


class FieldCreateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.url = reverse('create_field')  # Замените на ваш URL name
        self.form_data = {
            'title': 'Test Field',
            'description': 'Test Description',
            'cols': 5,
            'rows': 5
        }

    def test_get_create_view(self):
        request = self.factory.get(self.url)
        request.user = self.user
        response = FieldCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_post_create_view_without_file(self):
        request = self.factory.post(self.url, self.form_data)
        request.user = self.user
        response = FieldCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        field = Field.objects.first()
        self.assertEqual(field.title, 'Test Field')
        self.assertEqual(field.user, self.user)
        self.assertIsNone(field.file)

    def test_post_create_view_with_file(self):
        test_file = SimpleUploadedFile(
            "test.txt",
            b"Test file content",
            content_type="text/plain"
        )
        form_data = self.form_data.copy()
        form_data['file'] = test_file

        request = self.factory.post(self.url, form_data)
        request.user = self.user
        response = FieldCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)

        field = Field.objects.first()
        self.assertEqual(field.file.name, 'test.txt')
        self.assertEqual(field.file.data, b'Test file content')


class DownloadFileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.field_file = FieldFile.objects.create(
            name='test.txt',
            content_type='text/plain',
            data=b'Test content',
            size=12
        )
        self.url = reverse('download_file', args=[self.field_file.pk])  # Замените на ваш URL name

    def test_download_file(self):
        request = self.factory.get(self.url)
        response = download_file(request, self.field_file.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="test.txt"'
        )
        self.assertEqual(response.content, b'Test content')

    def test_download_nonexistent_file(self):
        request = self.factory.get(self.url + '999')  # Несуществующий ID
        response = download_file(request, 999)
        self.assertEqual(response.status_code, 404)