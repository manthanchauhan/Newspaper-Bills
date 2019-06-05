from django.contrib.auth.forms import UserCreationForm
from bill_manager import models


class SignUpForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ['username',
                  'email',
                  'password1',
                  'password2',
                  ]
