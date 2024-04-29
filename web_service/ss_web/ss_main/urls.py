from django.shortcuts import redirect
from .views import main
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main, name='main'),
]
