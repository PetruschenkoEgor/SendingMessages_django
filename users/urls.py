from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views

from django.urls import path

from users.apps import UsersConfig
from users.forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm
from users.views import UserCreateView, email_verification, UserDetailView, UserUpdateView

app_name = UsersConfig.name
urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('users/email-confirm/<str:token>/', email_verification, name='email-confirm'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html', email_template_name='password_reset_email.html', success_url='/password_reset/done/', form_class=CustomPasswordResetForm), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/reset/done/',
        form_class=CustomSetPasswordForm,
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('profile/<int:pk>/', UserDetailView.as_view(), name='profile'),
    path('profile/<int:pk>/edit/', UserUpdateView.as_view(), name='edit_user'),
]
