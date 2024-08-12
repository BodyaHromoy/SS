from . import views
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Авторизация
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Скауты
    path('my-cabinets/', views.user_cabinets, name='user_cabinets'),
    path('cabinet/<str:shkaf_id>/', views.cabinet_details, name='cabinet_details'),

    # Регистрация скаута
    path('create_courier/', create_courier, name='create_courier'),

    # Логисты
    path('assign_zone/', assign_zone_to_courier, name='assign_zone_to_courier'),
    path('delete_courier/<int:courier_id>/', views.delete_courier, name='delete_courier'),
    path('zones/', zone_list, name='zone_list'),
    path('zones/<int:zone_id>/', zone_detail, name='zone_detail'),
    path('zones/<int:zone_id>/cabinets/', cabinet_list, name='cabinet_list'),

    # Региональные менеджеры
    path('region/', main_region, name='main_region'),
    path('region_zones/<int:city_id>/', views.region_zones, name='region_zones'),
    path('region_logic/<int:zone_id>/', views.region_logic, name='region_logic'),
    path('create_logic/', create_logic, name='create_logic'),
    path('assign_logic/', assign_zone_to_logic, name='assign_zone_to_logic'),


    path('', views.new_eng, name='new_eng'),
    path('new_eng_cabinet/<str:shkaf_id>/', views.new_eng_cabinet_detail, name='new_eng_cabinet_detail'),


    path('123/', main, name='main'),

    # API
    path('api/station_ids', views.station_ids),
    path('api/cities', views.cities),
    path('api/zones', views.zones),
    path('api/my-cabinets/', views.user_cabinets_api, name='user_cabinets_api'),

    path('reports/', report, name='report'),
    path('reset_selection/', views.reset_selection, name='reset_selection'),

    path('api/cabinet/<str:shkaf_id>/details/', views.cabinet_details_api, name='cabinet_details_api'),  # Новый маршрут
]