from django import forms
from . import models


class EditPlanForm(forms.ModelForm):
    class Meta:
        model = models.Plan
        fields = ['sun',
                  'mon',
                  'tue',
                  'wed',
                  'thu',
                  'fri',
                  'sat',
                  ]