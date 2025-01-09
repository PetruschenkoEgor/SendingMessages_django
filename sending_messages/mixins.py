from django.contrib.auth.mixins import LoginRequiredMixin


class MailingFormMixin(LoginRequiredMixin):
    """Миксин для формы рассылки"""

    def get_form_kwargs(self):
        """При создании или редактировании рассылки, пользователь может выбрать только свои сообщения и получателей"""

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
