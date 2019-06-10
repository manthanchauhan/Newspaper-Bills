from django import forms
from django_summernote.widgets import SummernoteWidget


class FeedbackForm(forms.Form):
    username = forms.CharField(label='Username', required=True, disabled=True,
                               widget=forms.TextInput(
                                   attrs={'placeholder': 'Your username'}
                               ))
    email = forms.EmailField(label='Email id', required=True, disabled=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'Your registered e-mail id'}
                             ))
    subject = forms.CharField(label='Subject', max_length=100, required=True,
                              widget=forms.TextInput(
                                  attrs={'placeholder': 'What is the issue?'}
                              ))
    message = forms.CharField(label='Message', required=True,
                              widget=SummernoteWidget)

    image = forms.ImageField(required=False, label='Upload an image',
                             help_text='Provide an optional image or screen-shot')
