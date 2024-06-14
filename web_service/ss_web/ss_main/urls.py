from . import views
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('my-cabinets/', views.user_cabinets, name='user_cabinets'),
    path('cabinet/<str:shkaf_id>/', views.cabinet_details, name='cabinet_details'),

    path('create_courier/', create_courier, name='create_courier'),
    path('assign_zone/', assign_zone_to_courier, name='assign_zone_to_courier'),
    path('zones/', zone_list, name='zone_list'),
    path('zones/<int:zone_id>/', zone_detail, name='zone_detail'),
    path('zones/<int:zone_id>/cabinets/', cabinet_list, name='cabinet_list'),

    path('region/', main_region, name='main_region'),


    path('', main, name='main'),

    path('api/station_ids', views.station_ids),
    path('api/cities', views.cities),
    path('api/zones', views.zones),
    path('api/my-cabinets/', views.user_cabinets_api, name='user_cabinets_api'),

    path('reports/', report, name='report'),
    path('reset_selection/', views.reset_selection, name='reset_selection'),

    path('api/cabinet/<str:shkaf_id>/details/', views.cabinet_details_api, name='cabinet_details_api'),  # Новый маршрут
]