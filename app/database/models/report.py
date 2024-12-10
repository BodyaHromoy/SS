from app.database.database_connect import *



class Ss_main_report(BaseModel2):
    stationid = CharField(null=True, column_name='stationid')
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
    temp_cur1 = CharField(null=True, column_name='temp_cur1')
    temp_cur2 = CharField(null=True, column_name='temp_cur2')
    total_capacity = CharField(null=True, column_name='total_capacity')
    vid = CharField(null=True, column_name='vid')
    voltage_cur = CharField(null=True, column_name='voltage_cur')
    session_start = DateTimeField(null=True, column_name='session_start')
    time = DateTimeField(null=True, column_name='time')
    reason = CharField(null=True, column_name='reason')
    city = CharField(max_length=255, null=True)
    zone = CharField(max_length=255, null=True)
    start_percent = CharField(max_length=255, null=True)


# Создание таблицы
db2.create_tables([Ss_main_report])
