from django.contrib.auth.views import LoginView, LogoutView

from django.urls import path

from users.apps import UsersConfig
from users.forms import CustomAuthenticationForm

app_name = UsersConfig.name
urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
