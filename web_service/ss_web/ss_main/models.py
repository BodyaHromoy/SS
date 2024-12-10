from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class UserSession(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('courier', 'Courier'),
        ('logistician', 'Logistician'),
        ('regional_manager', 'Regional Manager'),
        ('engineer', 'Engineer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='courier')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        return f'{self.username} - {self.role}'


class Vendor(models.Model):
    vendor_name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.vendor_name


class City(models.Model):
    city_name = models.CharField(max_length=255, unique=True, null=False)
    country = models.CharField(max_length=255, null=False)
    vendor = models.ForeignKey(to=Vendor, on_delete=models.CASCADE, null=False, to_field='vendor_name')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='citys')


    def __str__(self):
        return self.city_name


class Zone(models.Model):
    zone_name = models.CharField(max_length=255, unique=True, null=False)
    city = models.ForeignKey(to=City, on_delete=models.CASCADE, null=False, to_field='city_name')
    vendor = models.ForeignKey(to=Vendor, on_delete=models.CASCADE, null=False, to_field='vendor_name')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='zones')

    def __str__(self):
        return self.zone_name

    def cell_status_counts(self):
        cabinets = Cabinet.objects.filter(zone=self)
        ready = Cell.objects.filter(cabinet_id__in=cabinets, status='ready').count()
        charging = Cell.objects.filter(cabinet_id__in=cabinets, status='charging').count()
        empty = Cell.objects.filter(cabinet_id__in=cabinets, status='empty').count()
        Inactive = Cell.objects.filter(cabinet_id__in=cabinets, status='Inactive').count()
        return {'ready': ready, 'charging': charging, 'empty': empty, 'Inactive': Inactive}


class Cabinet(models.Model):
    city = models.ForeignKey(to=City, on_delete=models.CASCADE, null=False, to_field='city_name')
    shkaf_id = models.CharField(null=False, unique=True, max_length=255)
    zone = models.ForeignKey(to=Zone, on_delete=models.CASCADE, null=False, to_field='zone_name')
    location = models.TextField()
    street = models.TextField()
    extra_inf = models.TextField()
    vendor = models.ForeignKey(to=Vendor, on_delete=models.CASCADE, null=False, to_field='vendor_name')

    def __str__(self):
        return self.shkaf_id


class Cell(models.Model):
    endpointid = models.IntegerField(verbose_name='EndpointID')
    cabinet_id = models.ForeignKey(to=Cabinet, on_delete=models.CASCADE, null=False, to_field='shkaf_id')
    balance_status = models.CharField(max_length=255, null=True, verbose_name='BALANCE_STATUS')
    capacity = models.CharField(max_length=255, null=True, verbose_name='CAPACITY')
    cap_coulo = models.CharField(max_length=255, null=True, verbose_name='CAP_COULO')
    cap_percent = models.CharField(max_length=255, null=True, verbose_name='CAP_PERCENT')
    start_percent = models.CharField(max_length=255, null=True, verbose_name='START_PERCENT')
    cap_vol = models.CharField(max_length=255, null=True, verbose_name='CAP_VOL')
    charge_cap_h = models.CharField(max_length=255, null=True, verbose_name='CHARGE_CAP_H')
    charge_cap_l = models.CharField(max_length=255, null=True, verbose_name='CHARGE_CAP_L')
    charge_times = models.CharField(max_length=255, null=True, verbose_name='CHARGE_TIMES')
    core_volt = models.CharField(max_length=255, null=True, verbose_name='CORE_VOLT')
    current_cur = models.CharField(max_length=255, null=True, verbose_name='CURRENT_CUR')
    cycle_times = models.CharField(max_length=255, null=True, verbose_name='CYCLE_TIMES')
    design_voltage = models.CharField(max_length=255, null=True, verbose_name='DESIGN_VOLTAGE')
    fun_boolean = models.CharField(max_length=255, null=True, verbose_name='FUN_BOOLEAN')
    healthy = models.CharField(max_length=255, null=True, verbose_name='HEALTHY')
    ochg_state = models.CharField(max_length=255, null=True, verbose_name='OCHG_STATE')
    odis_state = models.CharField(max_length=255, null=True, verbose_name='ODIS_STATE')
    over_discharge_times = models.CharField(max_length=255, null=True, verbose_name='OVER_DISCHARGE_TIMES')
    pcb_ver = models.CharField(max_length=255, null=True, verbose_name='PCB_VER')
    remaining_cap = models.CharField(max_length=255, null=True, verbose_name='REMAINING_CAP')
    remaining_cap_percent = models.CharField(max_length=255, null=True, verbose_name='REMAINING_CAP_PERCENT')
    sn = models.CharField(max_length=255, null=True, verbose_name='SN')
    sw_ver = models.CharField(max_length=255, null=True, verbose_name='SW_VER')
    temp_cur1 = models.CharField(max_length=255, null=True, verbose_name='TEMP_CUR1')
    temp_cur2 = models.CharField(max_length=255, null=True, verbose_name='TEMP_CUR2')
    total_capacity = models.CharField(max_length=255, null=True, verbose_name='TOTAL_CAPACITY')
    vid = models.CharField(max_length=255, null=True, verbose_name='VID')
    voltage_cur = models.CharField(max_length=255, null=True, verbose_name='VOLTAGE_CUR')
    session_start = models.DateTimeField(null=True, verbose_name='SESSION_START')
    session_end = models.DateTimeField(null=True, verbose_name='SESSION_END')
    status = models.CharField(max_length=255, null=True, verbose_name='STATUS')
    time = models.DateTimeField(null=True, verbose_name='time')
    vir_sn_eid = models.TextField(null=True, verbose_name='VIR_SN_EID')
    is_error = models.BooleanField(default=False, verbose_name='IS_ERROR')
    message = models.CharField(max_length=255, null=True, verbose_name='MESSAGE')

    def __str__(self):
        return self.vir_sn_eid


class Report(models.Model):
    stationid = models.CharField(null=True)
    balance_status = models.CharField(max_length=255, null=True)
    capacity = models.CharField(max_length=255, null=True)
    cap_coulo = models.CharField(max_length=255, null=True)
    cap_percent = models.CharField(max_length=255, null=True)
    cap_vol = models.CharField(max_length=255, null=True)
    charge_cap_h = models.CharField(max_length=255, null=True)
    charge_cap_l = models.CharField(max_length=255, null=True)
    charge_times = models.CharField(max_length=255, null=True)
    core_volt = models.CharField(max_length=255, null=True)
    current_cur = models.CharField(max_length=255, null=True)
    cycle_times = models.CharField(max_length=255, null=True)
    design_voltage = models.CharField(max_length=255, null=True)
    fun_boolean = models.CharField(max_length=255, null=True)
    healthy = models.CharField(max_length=255, null=True)
    ochg_state = models.CharField(max_length=255, null=True)
    odis_state = models.CharField(max_length=255, null=True)
    over_discharge_times = models.CharField(max_length=255, null=True)
    pcb_ver = models.CharField(max_length=255, null=True)
    remaining_cap = models.CharField(max_length=255, null=True)
    remaining_cap_percent = models.CharField(max_length=255, null=True)
    sn = models.CharField(max_length=255, null=True)
    sw_ver = models.CharField(max_length=255, null=True)
    temp_cur1 = models.CharField(max_length=255, null=True)
    temp_cur2 = models.CharField(max_length=255, null=True)
    total_capacity = models.CharField(max_length=255, null=True)
    vid = models.CharField(max_length=255, null=True)
    voltage_cur = models.CharField(max_length=255, null=True)
    session_start = models.DateTimeField(null=True, verbose_name='SESSION_START')
    time = models.DateTimeField(null=True, verbose_name='time')
    reason = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    zone = models.CharField(max_length=255, null=True)
    start_percent = models.CharField(max_length=255, null=True)

    class Meta:
        app_label = 'ss_main'


class Marked(models.Model):
    sn = models.CharField(max_length=255, null=True, verbose_name='SN')


class big_battary_list(models.Model):
    sn = models.CharField(max_length=255, null=True, verbose_name='SN')
    year = models.CharField(max_length=255, null=True, verbose_name='YEAR')
    cycle_times = models.CharField(max_length=255, null=True, verbose_name='CYCLE_TIMES')
    is_tired = models.BooleanField(default=False, verbose_name='IS_TIRED')


class Cabinet_settings_for_auto_marking (models.Model):
    settings_for = models.CharField(max_length=255, null=True, verbose_name='SETTINGS_FOR', unique=True)
    cabinet_id = models.ForeignKey(to=Cabinet, on_delete=models.CASCADE, null=False, to_field='shkaf_id')
    sn_error = models.BooleanField(default=False, verbose_name='SN_ERROR')
    year_of_manufacture = models.CharField(max_length=255, null=True)
    max_cycle_times = models.CharField(null=True)
    vid = models.CharField(max_length=255, null=True)
    sw_ver = models.CharField(max_length=255, null=True)
    critical_temp = models.IntegerField(null=True)
    lock_status = models.BooleanField(default=False, verbose_name='LOCK_STATUS')
    temp_inside = models.IntegerField(null=True)
    fan_status = models.BooleanField(default=False, verbose_name='FAN_STATUS')
    mains_voltage = models.CharField(max_length=255, null=True)
    reserve_voltage = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.settings_for


class Settings_for_settings (models.Model):
    settings_for = models.ForeignKey(to=Cabinet_settings_for_auto_marking, on_delete=models.CASCADE, null=False, to_field='settings_for')
    sn_error = models.BooleanField(default=False, verbose_name='SN_ERROR')
    year_of_manufacture = models.BooleanField(default=False, verbose_name='YEAR_OF_MANUFACTURE')
    max_cycle_times = models.BooleanField(default=False, verbose_name='MAX_CYCLE_TIMES')
    vid = models.BooleanField(default=False, verbose_name='VID')
    sw_ver = models.BooleanField(default=False, verbose_name='SW_VER')

    def __str__(self):
        return self.settings_for





