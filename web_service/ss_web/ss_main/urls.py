from django.urls import path
import ss_main.views as views

urlpatterns = [
    path('', views.main, name='main'),
]
