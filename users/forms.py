from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from sending_messages.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """ Форма регистрации пользователя """

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class CustomAuthenticationForm(StyleFormMixin, AuthenticationForm):
    """ Форма входа """

    class Meta:
        model = User
        field = ('email', 'password')
