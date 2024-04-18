from app.database.database_connect import *
from app.database.models.cabinets import Cabinet


class Cell(BaseModel):
    endpointid = IntegerField(primary_key=True, column_name='EndpointID')
    cabinet = ForeignKeyField(Cabinet, backref='cells', on_delete='CASCADE')  # Добавляем внешний ключ к шкафу
    stationid = IntegerField(null=True, column_name='StationID')
    balance_status = CharField(null=True, column_name='BALANCE_STATUS')
    capacity = CharField(null=True, column_name='CAPACITY')
    cap_coulo = CharField(null=True, column_name='CAP_COULO')
    cap_percent = CharField(null=True, column_name='CAP_PERCENT')
    cap_vol = CharField(null=True, column_name='CAP_VOL')
    charge_cap_h = CharField(null=True, column_name='CHARGE_CAP_H')
    charge_cap_l = CharField(null=True, column_name='CHARGE_CAP_L')
    charge_times = CharField(null=True, column_name='CHARGE_TIMES')
    core_volt = CharField(null=True, column_name='CORE_VOLT')
    current_cur = CharField(null=True, column_name='CURRENT_CUR')
    cycle_times = CharField(null=True, column_name='CYCLE_TIMES')
    design_voltage = CharField(null=True, column_name='DESIGN_VOLTAGE')
    fun_boolean = CharField(null=True, column_name='FUN_BOOLEAN')
    healthy = CharField(null=True, column_name='HEALTHY')
    ochg_state = CharField(null=True, column_name='OCHG_STATE')
    odis_state = CharField(null=True, column_name='ODIS_STATE')
    over_discharge_times = CharField(null=True, column_name='OVER_DISCHARGE_TIMES')
    pcb_ver = CharField(null=True, column_name='PCB_VER')
    remaining_cap = CharField(null=True, column_name='REMAINING_CAP')
    remaining_cap_percent = CharField(null=True, column_name='REMAINING_CAP_PERCENT')
    sn = CharField(null=True, column_name='SN')
    sw_ver = CharField(null=True, column_name='SW_VER')
    temp_cur1 = CharField(null=True, column_name='TEMP_CUR1')
    temp_cur2 = CharField(null=True, column_name='TEMP_CUR2')
    total_capacity = CharField(null=True, column_name='TOTAL_CAPACITY')
    vid = CharField(null=True, column_name='VID')
    voltage_cur = CharField(null=True, column_name='VOLTAGE_CUR')
    session_start = CharField(null=True, column_name='SESSION_START')
    time = CharField(null=True, column_name='time')


# Создание таблицы
db.create_tables([Cell])
