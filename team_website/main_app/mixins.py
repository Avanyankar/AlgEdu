from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy('login')
    raise_exception = False

    def test_func(self):
        return self.request.user.is_staff


class SuperuserRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy('login')
    raise_exception = True

    def test_func(self):
        return self.request.user.is_superuser