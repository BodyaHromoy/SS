from django.shortcuts import redirect

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

    path('', main, name='main'),
    path('api/station_ids', views.station_ids),
    path('api/cities', views.cities),
    path('api/zones', views.zones),
    path('reports/', report, name='report'),

    path('reset_selection/', views.reset_selection, name='reset_selection'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)