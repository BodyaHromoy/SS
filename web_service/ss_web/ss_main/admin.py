from django.contrib import admin

from .models import *

admin.site.register(Cell)
admin.site.register(Cabinet)
admin.site.register(Report)
admin.site.register(City)
admin.site.register(Vendor)


class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_name', 'city', 'vendor')
    search_fields = ('zone_name', 'city__city_name', 'vendor__vendor_name')
    filter_horizontal = ('users',)


admin.site.register(Zone, ZoneAdmin)
