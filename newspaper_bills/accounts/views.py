from django.shortcuts import render, redirect
from django.views.generic import View
from . import forms
from django.contrib.auth import login
from django.contrib import messages


class SignUp(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            return redirect('bill_manager:home')

        form = forms.SignUpForm()
        messages.info(request, 'To access this web-app it is mandatory to create an '
                               'account.', fail_silently=True)
        return render(request, 'signup.html', {'form': form})

    @staticmethod
    def post(request):
        form = forms.SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Sign-Up was successful!\n')
            messages.info(request, 'Please add your newspaper plan, this step is needed '
                                   'to be performed now.')
            return redirect('bill_manager:home')

        else:
            return render(request, 'signup.html', {'form': form})
