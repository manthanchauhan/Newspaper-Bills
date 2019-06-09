from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from . import forms
from . import models
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class FeedbackView(LoginRequiredMixin, View):
    login_url = 'login'
    form_class = forms.FeedbackForm
    template = 'feedback/form.html'

    def get(self, request):
        initial = {'username': request.user.username,
                   'email': request.user.email}
        form = self.form_class(initial=initial)
        return render(request, self.template, {'form': form})

    def post(self, request):
        print(request.POST)
        form = self.form_class(request.POST, request.FILES)
        # print(form.is_valid())

        if form.is_valid():
            form = form.cleaned_data

            image = request.FILES.get('image', None)
            feedback = models.Feedback.objects.create(user=request.user,
                                                      subject=form['subject'],
                                                      message=form['message'],
                                                      image=image,
                                                      )
            messages.success(request, 'You feedback has been submitted successfully!')
            self.send_mail_to_operations(feedback)
            self.send_mail_to_user(feedback)
            return redirect('bill_manager:home')

        else:
            form = self.form_class(request.POST, request.FILES)
            return render(request, self.template, {'form': form})

    def send_mail_to_user(self, feedback):
        subject = 'Feedback submitted successfully'
        message_template = 'feedback/user_email.html'
        message = render_to_string(message_template, {'user': self.request.user,
                                                      'feedback_id': feedback.id,
                                                      'app_name': 'Newspaper Bills',
                                                      })
        text_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to = self.request.user.email
        send_mail(subject=subject, message=text_message, from_email=from_email,
                  recipient_list=[to], fail_silently=True, html_message=message)

    def send_mail_to_operations(self, feedback):
        subject = 'feedback submitted by ' + self.request.user.username
        message_template = 'feedback/operations_email.html'
        message = render_to_string(message_template, {'user': self.request.user,
                                                      'feedback': feedback
                                                      })
        text_message = strip_tags(message)
        from_email = settings.EMAIL_HOST_USER
        to = settings.OPERATIONS_EMAIL
        send_mail(subject=subject, message=text_message, from_email=from_email,
                  recipient_list=[to], fail_silently=True, html_message=message)



