from django.shortcuts import redirect

from . import views
from .views import main, CustomLoginView, CustomLogoutView, report
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import report


urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('', main, name='main'),

    path('reports/', report, name='report'),

    path('reset_selection/', views.reset_selection, name='reset_selection'),
]
