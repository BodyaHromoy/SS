from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(Cell)
admin.site.register(Cabinet)
admin.site.register(Report)
admin.site.register(City)
admin.site.register(Vendor)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')  # добавлено 'role'
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )


class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_name', 'city', 'vendor')
    search_fields = ('zone_name', 'city__city_name', 'vendor__vendor_name')
    filter_horizontal = ('users',)


admin.site.register(Zone, ZoneAdmin)
admin.site.register(CustomUser, CustomUserAdmin)