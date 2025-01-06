import secrets

from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    """ Регистрация пользователя """

    model = User
    form_class = UserRegisterForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """ Подтверждение почты после успешной регистрации  """

        user = form.save()
        # Делаем пользователя неактивным
        user.is_active = False
        # генерируем токен с помощью библиотеки secrets(16 символов)
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        # откуда пришел пользователь
        host = self.request.get_host()
        # генерируем пользователю ссылку для перехода, она отправится пользователю
        url = f'http://{host}/users/email-confirm/{token}/'
        # отправка сообщения
        send_mail(
            subject='Подтверждение почты',
            message=f'Привет, перейди по ссылке для подтверждения почты {url}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    login(request, user)
    return redirect(reverse('sending_messages:home'))


class UserDetailView(DetailView):
    """ Просмотр пользователя """

    model = User
    template_name = 'profile.html'
    context_object_name = 'user'


# class UserUpdateView(UpdateView):
#     """ Редактирование пользователя """
#
#     model = User
