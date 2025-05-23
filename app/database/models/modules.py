from app.database.database_connect import *
from app.database.models.cabinets import Ss_main_cabinet


class ss_main_cell(BaseModel):
    endpointid = IntegerField(column_name='endpointid')
    cabinet_id_id = ForeignKeyField(Ss_main_cabinet, field=Ss_main_cabinet.shkaf_id, on_delete='CASCADE')
    balance_status = CharField(null=True, column_name='balance_status')
    capacity = CharField(null=True, column_name='capacity')
    cap_coulo = CharField(null=True, column_name='cap_coulo')
    cap_percent = CharField(null=True, column_name='cap_percent')
    cap_vol = CharField(null=True, column_name='cap_vol')
    charge_cap_h = CharField(null=True, column_name='charge_cap_h')
    charge_cap_l = CharField(null=True, column_name='charge_cap_l')
    charge_times = CharField(null=True, column_name='charge_times')
    core_volt = CharField(null=True, column_name='core_volt')
    current_cur = CharField(null=True, column_name='current_cur')
    cycle_times = CharField(null=True, column_name='cycle_times')
    design_voltage = CharField(null=True, column_name='design_voltage')
    fun_boolean = CharField(null=True, column_name='fun_boolean')
    healthy = CharField(null=True, column_name='healthy')
    ochg_state = CharField(null=True, column_name='ochg_state')
    odis_state = CharField(null=True, column_name='odis_state')
    over_discharge_times = CharField(null=True, column_name='over_discharge_times')
    pcb_ver = CharField(null=True, column_name='pcb_ver')
    remaining_cap = CharField(null=True, column_name='remaining_cap')
    remaining_cap_percent = CharField(null=True, column_name='remaining_cap_percent')
    sn = CharField(null=True, column_name='sn')
    sw_ver = CharField(null=True, column_name='sw_ver')
    sw_name = CharField(null=True, column_name='sw_name')
    temp_cur1 = CharField(null=True, column_name='temp_cur1')
    temp_cur2 = CharField(null=True, column_name='temp_cur2')
    total_capacity = CharField(null=True, column_name='total_capacity')
    vid = CharField(null=True, column_name='vid')
    voltage_cur = CharField(null=True, column_name='voltage_cur')
    session_start = CharField(null=True, verbose_name='session_start')
    session_end = CharField(null=True, verbose_name='session_end')
    status = CharField(null=True, verbose_name='status')
    time = CharField(null=True, column_name='time')
    vir_sn_eid = TextField(null=True, verbose_name='VIR_SN_EID')
    is_error = BooleanField(null=True, verbose_name='is_error', default=False)
    message = CharField(null=True, verbose_name='MESSAGE')
    start_percent = CharField(max_length=255, null=True, verbose_name='START_PERCENT')


class ss_main_marked(BaseModel):
    sn = CharField(null=True, verbose_name='SN')


class ss_main_big_battary_list(BaseModel):
    sn = CharField(max_length=255, null=True, verbose_name='SN')
    year = CharField(max_length=255, null=True, verbose_name='YEAR')
    cycle_times = CharField(max_length=255, null=True, verbose_name='CYCLE_TIMES')
    is_tired = BooleanField(default=False, verbose_name='IS_TIRED')


class ss_main_cabinet_settings_for_auto_marking(BaseModel):
    settings_for = CharField(max_length=255, null=True, verbose_name='SETTINGS_FOR', unique=True)
    cabinet_id_id = ForeignKeyField(Ss_main_cabinet, field=Ss_main_cabinet.shkaf_id, on_delete='CASCADE')
    sn_error = BooleanField(default=False, verbose_name='SN_ERROR')
    year_of_manufacture = CharField(max_length=255, null=True)
    max_cycle_times = IntegerField(null=True)
    vid = CharField(max_length=255, null=True)
    sw_ver = CharField(max_length=255, null=True)
    critical_temp = IntegerField(null=True)
    lock_status = BooleanField(default=False, verbose_name='LOCK_STATUS')
    temp_inside = IntegerField(null=True)
    fan_status = BooleanField(default=False, verbose_name='FAN_STATUS')
    mains_voltage = CharField(max_length=255, null=True)
    reserve_voltage = CharField(max_length=255, null=True)


class ss_main_settings_for_settings(BaseModel):
    settings_for_id = ForeignKeyField(ss_main_cabinet_settings_for_auto_marking, field=ss_main_cabinet_settings_for_auto_marking.settings_for, on_delete='CASCADE')
    sn_error = BooleanField(default=False, verbose_name='SN_ERROR')
    year_of_manufacture = BooleanField(default=False, verbose_name='YEAR_OF_MANUFACTURE')
    max_cycle_times = BooleanField(default=False, verbose_name='MAX_CYCLE_TIMES')
    vid = BooleanField(default=False, verbose_name='VID')
    sw_ver = BooleanField(default=False, verbose_name='SW_VER')


class ss_main_cabinet_history (BaseModel):
    history_for = ForeignKeyField(Ss_main_cabinet, field=Ss_main_cabinet.shkaf_id, on_delete='CASCADE')
    first_half = IntegerField(verbose_name='FIRST_HALF', default=0)
    second_half = IntegerField(verbose_name='SECOND_HALF', default=0)
    first_data = TextField(null=True)
    second_data = TextField(null=True)
    date = DateTimeField(null=True)