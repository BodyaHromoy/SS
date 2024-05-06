from django.contrib.auth.views import LoginView, LogoutView
from .decorators.auth_decorators import staff_required
from .forms.auth_form import CustomAuthenticationForm
from django.shortcuts import render
from .models import User


# @staff_required
def main(request):
    return render(request, 'ss_main/base.html', {})


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'ss_main/login.html'

    def get_success_url(self):
        return self.request.GET.get('next', '/')


class CustomLogoutView(LogoutView):
    next_page = '/'
    http_method_names = ['post']
