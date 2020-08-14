from django.urls import path, re_path
from django.shortcuts import redirect

from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('register/', views.register, name='register'),
]

