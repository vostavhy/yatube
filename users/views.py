from django.shortcuts import redirect, render
from django.core import mail
from django.views.generic import CreateView

from .forms import CreationForm


class SignUP(CreateView):
    form_class = CreationForm
    success_url = '/auth/login/'
    template_name = 'registration/signup.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            subject = f"Greetings {user.username}"
            message = f"Greetings {user.username} on our site! Your registration was successfully confirmed!"
            to_mail = user.email_user
            from_email = 'example@my_email.com'

            mail.send_mail(
                subject=subject, message=message,
                from_email=from_email, recipient_list=[to_mail],
                fail_silently=False,  # выводить описание ошибок
            )

            return redirect('login')

        return render(request, self.template_name, {'form': form})
