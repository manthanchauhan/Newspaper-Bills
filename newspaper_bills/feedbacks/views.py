from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.views.generic import FormView

from . import forms
from . import models


class FeedbackView(LoginRequiredMixin, FormView):
    login_url = settings.LOGIN_URL
    form_class = forms.FeedbackForm
    template_name = 'feedback/form.html'
    success_url = 'bill_manager:home'

    def get_initial(self):
        return {'username': self.request.user.username,
                'email': self.request.user.email
                }

    def form_valid(self, form):
        for file in self.request.FILES.keys():
            print(file)
        image = self.request.FILES.get('image', None)
        form_data = form.cleaned_data
        feedback = models.Feedback.objects.create(user=self.request.user,
                                                  subject=form_data['subject'],
                                                  message=form_data['message'],
                                                  image=image,
                                                  )
        messages.success(self.request, 'You feedback has been submitted successfully!')
        self.send_mail_to_operations(feedback)
        return redirect(self.success_url)

    def send_mail_to_operations(self, feedback):
        subject = 'feedback submitted by ' + self.request.user.username
        message_template = 'feedback/operations_email.html'
        message = render_to_string(message_template, {'user': self.request.user,
                                                      'feedback': feedback
                                                      })
        from_email = settings.EMAIL_HOST_USER
        to = settings.OPERATIONS_EMAIL
        email = EmailMessage(subject=subject, body=message, from_email=from_email,
                             to=[to])
        email.content_subtype = 'html'

        try:
            email.attach_file(path=feedback.image.url[1:])
        except ValueError:
            pass
        email.send(fail_silently=True)



