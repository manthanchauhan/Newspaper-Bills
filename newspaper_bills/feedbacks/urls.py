from django.urls import path
from . import views


app_name = 'feedbacks'
urlpatterns = [
    path('', views.FeedbackView.as_view(), name='feedback_form'),
]
