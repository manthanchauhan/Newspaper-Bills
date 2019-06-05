"""newspaper_bills URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bill_manager import views as bill_manager_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bill_manager_views.Home.as_view(), name='home'),
    path('plan/', bill_manager_views.Plan.as_view(), name='plan'),
    path('edit_plan/', bill_manager_views.EditPlan.as_view(), name='edit_plan'),
    path('my_bills/', bill_manager_views.MyBills.as_view(), name='my_bills'),
    path('bill/<int:pk>/', bill_manager_views.Bill.as_view(), name='bill'),
]
