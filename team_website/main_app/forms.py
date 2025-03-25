from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'location', 'birth_date', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }
        labels = {
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'email': _('Email'),
            'location': _('Местоположение'),
            'birth_date': _('Дата рождения'),
            'bio': _('О себе'),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Этот email уже используется'))
        return email

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date.year < 1900:
            raise ValidationError(_('Некорректная дата рождения'))
        return birth_date