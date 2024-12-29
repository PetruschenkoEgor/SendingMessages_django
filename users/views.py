from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    """ Регистрация пользователя """

    model = User
    form_class = UserRegisterForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('sending_messages:home')

    def form_valid(self, form):
        """ Автоматический вход после успешной регистрации """

        response = super().form_valid(form)
        user = self.object
        # вход в систему
        login(self.request, user)
        return response
