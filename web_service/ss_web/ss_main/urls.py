from django.shortcuts import redirect
from django.template.defaulttags import url
from django.views.generic import RedirectView

from . import views
from .views import main, CustomLoginView, CustomLogoutView, report
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import report
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('my-cabinets/', views.user_cabinets, name='user_cabinets'),
    path('cabinet/<str:shkaf_id>/', views.cabinet_details, name='cabinet_details'),
    path('', main, name='main'),
    path('api/station_ids', views.station_ids),
    path('api/cities', views.cities),
    path('api/zones', views.zones),
    path('reports/', report, name='report'),
    path('reset_selection/', views.reset_selection, name='reset_selection'),
    path('api/cabinet/<str:shkaf_id>/details/', views.cabinet_details_api, name='cabinet_details_api'),  # Новый маршрут
]