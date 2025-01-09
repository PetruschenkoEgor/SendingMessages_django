from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm

from sending_messages.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Форма регистрации пользователя"""

    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        labels = {
            "password1": "Пароль",
            "password2": "Повторите пароль",
        }


class CustomAuthenticationForm(StyleFormMixin, AuthenticationForm):
    """Форма входа"""

    class Meta:
        model = User
        fields = ("email", "password")
        labels = {
            "password": "Пароль",
        }


class UserUpdateForm(StyleFormMixin, forms.ModelForm):
    """Форма редактирования пользователя"""

    class Meta:
        model = User
        fields = ("avatar", "phone_number", "country")


class CustomPasswordResetForm(StyleFormMixin, PasswordResetForm):
    """Форма для запроса сброса пароля"""

    pass


class CustomSetPasswordForm(StyleFormMixin, SetPasswordForm):
    """Форма для установки нового пароля"""

    pass
