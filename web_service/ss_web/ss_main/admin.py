from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(Cell)
admin.site.register(Cabinet)
admin.site.register(Report)
admin.site.register(Vendor)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')

    # 👇 Добавляем assigned_zones в горизонтальную фильтрацию
    filter_horizontal = ("groups", "user_permissions", "assigned_zones")

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
        ("Зоны пользователя", {
            "fields": ('assigned_zones',),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )


class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_name', 'city', 'vendor')
    search_fields = ('zone_name', 'city__city_name', 'vendor__vendor_name')
    filter_horizontal = ('users',)


class CityAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'country', 'vendor')
    search_fields = ['city_name']
    filter_horizontal = ('users',)


admin.site.register(Zone, ZoneAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Cabinet_settings_for_auto_marking)
admin.site.register(Settings_for_settings)
admin.site.register(CustomUser, CustomUserAdmin)
