from django.urls import path
from . import views

app_name = 'bill_manager'
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('plan/<int:pk>/', views.Plan.as_view(), name='plan'),
    path('edit_plan/<int:pk>/', views.EditPlan.as_view(), name='edit_plan'),
    path('my_bills/', views.MyBills.as_view(), name='my_bills'),
    path('bill/<int:pk>/', views.Bill.as_view(), name='bill'),
    path('create_plan/', views.NewPlan.as_view(), name='create_plan'),
]
