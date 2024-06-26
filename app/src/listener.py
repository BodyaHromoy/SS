import asyncio
import datetime
import json

from paho.mqtt.client import Client
import pytz


from app.database.models.modules import ss_main_cell
from app.database.models.report import Ss_main_report
from app.database.models.cabinets import Ss_main_cabinet


active_v_sn = {}


def update_entry(existing_entry, stat_id, status_data):
    import datetime

    almaty_timezone = pytz.timezone('Asia/Almaty')
    time_wth_tzinfo = datetime.datetime.now(almaty_timezone)
    current_time = time_wth_tzinfo.replace(tzinfo=None)
    existing_entry.cabinet_id_id = stat_id
    existing_entry.balance_status = status_data.get("BALANCE_STATUS")
    existing_entry.capacity = status_data.get("CAPACITY")
    existing_entry.cap_coulo = status_data.get("CAP_COULO")
    cap_percent = int(status_data.get("CAP_PERCENT", "0")) if status_data.get("CAP_PERCENT") else 0
    existing_entry.cap_percent = cap_percent
    existing_entry.cap_vol = status_data.get("CAP_VOL")
    existing_entry.charge_cap_h = status_data.get("CHARGE_CAP_H")
    existing_entry.charge_cap_l = status_data.get("CHARGE_CAP_L")
    existing_entry.charge_times = status_data.get("CHARGE_TIMES")
    existing_entry.core_volt = status_data.get("CORE_VOLT")
    existing_entry.current_cur = status_data.get("CURRENT_CUR")
    existing_entry.cycle_times = status_data.get("CYCLE_TIMES")
    existing_entry.design_voltage = status_data.get("DESIGN_VOLTAGE")
    existing_entry.fun_boolean = status_data.get("FUN_BOOLEAN")
    existing_entry.healthy = status_data.get("HEALTHY")
    existing_entry.ochg_state = status_data.get("OCHG_STATE")
    existing_entry.odis_state = status_data.get("ODIS_STATE")
    existing_entry.over_discharge_times = status_data.get("OVER_DISCHARGE_TIMES")
    existing_entry.pcb_ver = status_data.get("PCB_VER")
    existing_entry.remaining_cap = status_data.get("REMAINING_CAP")
    existing_entry.remaining_cap_percent = status_data.get("REMAINING_CAP_PERCENT")
    existing_entry.sw_ver = status_data.get("SW_VER")
    existing_entry.temp_cur1 = status_data.get("TEMP_CUR1")
    existing_entry.temp_cur2 = status_data.get("TEMP_CUR2")
    existing_entry.total_capacity = status_data.get("TOTAL_CAPACITY")

    if "4e344007" in str(status_data.get("VID")):
        existing_entry.vid = "JET"
    elif "4e34300e" in str(status_data.get("VID")):
        existing_entry.vid = "WOOSH"
    elif "4e34400d" in str(status_data.get("VID")):
        existing_entry.vid = "YANDEX"
    elif "4e34400a" in str(status_data.get("VID")):
        existing_entry.vid = "SVING"
    elif "4e34300c" in str(status_data.get("VID")):
        existing_entry.vid = "VOI"
    else:
        existing_entry.vid = status_data.get("VID")

    existing_entry.voltage_cur = status_data.get("VOLTAGE_CUR")
    existing_entry.time = current_time
    existing_entry.sn = status_data.get("SN")

    if not existing_entry.session_start:
        existing_entry.session_start = current_time
    existing_entry.session_end = current_time
    if cap_percent >= 91:
        existing_entry.status = "ready"
    elif "4" in str(status_data.get("FUN_BOOLEAN")):
        existing_entry.status = "charging"
    else:
        existing_entry.status = "not_charging"

    existing_entry.save()
    print(f"Информация для {existing_entry.vir_sn_eid} обновлена.")


def move_to_report(existing_entry, reason):
    report_entry = Ss_main_report.create(
        stationid=existing_entry.vir_sn_eid,
        balance_status=existing_entry.balance_status,
        capacity=existing_entry.capacity,
        cap_coulo=existing_entry.cap_coulo,
        cap_percent=existing_entry.cap_percent,
        cap_vol=existing_entry.cap_vol,
        charge_cap_h=existing_entry.charge_cap_h,
        charge_cap_l=existing_entry.charge_cap_l,
        charge_times=existing_entry.charge_times,
        core_volt=existing_entry.core_volt,
        current_cur=existing_entry.current_cur,
        cycle_times=existing_entry.cycle_times,
        design_voltage=existing_entry.design_voltage,
        fun_boolean=existing_entry.fun_boolean,
        healthy=existing_entry.healthy,
        ochg_state=existing_entry.ochg_state,
        odis_state=existing_entry.odis_state,
        over_discharge_times=existing_entry.over_discharge_times,
        pcb_ver=existing_entry.pcb_ver,
        remaining_cap=existing_entry.remaining_cap,
        remaining_cap_percent=existing_entry.remaining_cap_percent,
        sn=existing_entry.sn,
        sw_ver=existing_entry.sw_ver,
        temp_cur1=existing_entry.temp_cur1,
        temp_cur2=existing_entry.temp_cur2,
        total_capacity=existing_entry.total_capacity,
        vid=existing_entry.vid,
        voltage_cur=existing_entry.voltage_cur,
        session_start=existing_entry.session_start,
        session_end=existing_entry.session_end,
        time=existing_entry.time,
        reason=reason,
        city=find_city_name(existing_entry.cabinet_id_id.city.city_name),
        zone=find_zone_name(existing_entry.cabinet_id_id.zone.zone_name)
    )
    print(f"Перемещена строка с Endpoint ID {existing_entry.vir_sn_eid} в отчет из-за {reason}.")


def find_city_name(city_name):
    try:
        cabinet = Ss_main_cabinet.get(Ss_main_cabinet.city == city_name)
        return cabinet.city.city_name
    except Ss_main_cabinet.DoesNotExist:
        print(f"Не удалось найти шкаф для города {city_name}")
        return None


def find_zone_name(zone_name):
    try:
        cabinet = Ss_main_cabinet.get(Ss_main_cabinet.zone == zone_name)
        return cabinet.zone.zone_name
    except Ss_main_cabinet.DoesNotExist:
        print(f"{zone_name} не найден.")
        return None


def create_new_entry(end_id, stat_id, sn=None, status_data=None, status="empty", vir_sn_eid="empty"):
    if ss_main_cell.select().where(ss_main_cell.vir_sn_eid == vir_sn_eid).exists():
        print(f"Запись с Endpoint ID {end_id} и Station ID {stat_id} уже существует.")
        return
    else:
        fun_boolean = status_data.get("FUN_BOOLEAN") if status_data else None
        cell_entry = ss_main_cell.create(
            endpointid=end_id,
            cabinet_id_id=stat_id,
            sn=sn,
            balance_status=status_data.get("BALANCE_STATUS") if status_data else None,
            capacity=status_data.get("CAPACITY") if status_data else None,
            cap_coulo=status_data.get("CAP_COULO") if status_data else None,
            cap_percent=status_data.get("CAP_PERCENT") if status_data else None,
            cap_vol=status_data.get("CAP_VOL") if status_data else None,
            charge_cap_h=status_data.get("CHARGE_CAP_H") if status_data else None,
            charge_cap_l=status_data.get("CHARGE_CAP_L") if status_data else None,
            charge_times=status_data.get("CHARGE_TIMES") if status_data else None,
            core_volt=status_data.get("CORE_VOLT") if status_data else None,
            current_cur=status_data.get("CURRENT_CUR") if status_data else None,
            cycle_times=status_data.get("CYCLE_TIMES") if status_data else None,
            design_voltage=status_data.get("DESIGN_VOLTAGE") if status_data else None,
            fun_boolean=fun_boolean,
            healthy=status_data.get("HEALTHY") if status_data else None,
            ochg_state=status_data.get("OCHG_STATE") if status_data else None,
            odis_state=status_data.get("ODIS_STATE") if status_data else None,
            over_discharge_times=status_data.get("OVER_DISCHARGE_TIMES") if status_data else None,
            pcb_ver=status_data.get("PCB_VER") if status_data else None,
            remaining_cap=status_data.get("REMAINING_CAP") if status_data else None,
            remaining_cap_percent=status_data.get("REMAINING_CAP_PERCENT") if status_data else None,
            sw_ver=status_data.get("SW_VER") if status_data else None,
            temp_cur1=status_data.get("TEMP_CUR1") if status_data else None,
            temp_cur2=status_data.get("TEMP_CUR2") if status_data else None,
            total_capacity=status_data.get("TOTAL_CAPACITY") if status_data else None,
            vid=status_data.get("VID") if status_data else None,
            voltage_cur=status_data.get("VOLTAGE_CUR") if status_data else None,
            status=status,
            vir_sn_eid=vir_sn_eid
        )
        print(f"Создана запись для {vir_sn_eid}.")


async def sort(msg):
    data = json.loads(msg.payload.decode('utf-8'))
    message_type = data.get('Type')

    if message_type == 'Ping':

        v_end_id = data.get("EndpointID")
        v_stat_id = data.get("StationID")
        end_id = data.get("EndpointID")
        stat_id = data.get("StationID")
        delimiter = "-"
        vir_sn = str(v_stat_id) + str(delimiter) + str(v_end_id)
        print(vir_sn)

        active_v_sn[vir_sn] = datetime.datetime.now()

        print("Получен пинг от ", vir_sn)
        existing_entry = ss_main_cell.select().where(ss_main_cell.vir_sn_eid == vir_sn).first()

        if existing_entry:
            if existing_entry.sn:
                move_to_report(existing_entry, reason="Ping")
                print("Скопирована существующая запись в отчет.")
                existing_entry.sn = None
                existing_entry.balance_status = None
                existing_entry.capacity = None
                existing_entry.cap_coulo = None
                existing_entry.cap_percent = None
                existing_entry.cap_vol = None
                existing_entry.charge_cap_h = None
                existing_entry.charge_cap_l = None
                existing_entry.charge_times = None
                existing_entry.core_volt = None
                existing_entry.current_cur = None
                existing_entry.cycle_times = None
                existing_entry.design_voltage = None
                existing_entry.fun_boolean = None
                existing_entry.healthy = None
                existing_entry.ochg_state = None
                existing_entry.odis_state = None
                existing_entry.over_discharge_times = None
                existing_entry.pcb_ver = None
                existing_entry.remaining_cap = None
                existing_entry.remaining_cap_percent = None
                existing_entry.sw_ver = None
                existing_entry.temp_cur1 = None
                existing_entry.temp_cur2 = None
                existing_entry.total_capacity = None
                existing_entry.vid = None
                existing_entry.voltage_cur = None
                existing_entry.session_start = None
                existing_entry.session_end = None
                existing_entry.time = None
                existing_entry.status = "empty"
                existing_entry.save()
                print("Обнулены поля существующей записи.")
            else:
                print("SN в записи пуст. Ничего не копируем в отчет.")
        else:
            create_new_entry(end_id, stat_id, status="empty", vir_sn_eid=vir_sn)
        return

    if message_type == 'Status':
        v_end_id = data.get("EndpointID")
        v_stat_id = data.get("StationID")
        end_id = data.get("EndpointID")
        stat_id = data.get("StationID")
        delimiter = "-"
        vir_sn = str(v_stat_id) + str(delimiter) + str(v_end_id)

        sn = data.get("Status", {}).get("SN")  # Получаем SN из поля "Status"
        existing_entry = ss_main_cell.select().where(ss_main_cell.vir_sn_eid == vir_sn).first()

        if existing_entry:
            update_entry(existing_entry, stat_id, data["Status"])
        else:
            create_new_entry(end_id, stat_id, sn, data["Status"], vir_sn_eid=vir_sn)
            print(f"Создана новая запись для {vir_sn}")
        active_v_sn[vir_sn] = datetime.datetime.now()
        return

    print("Неизвестный тип сообщения:", message_type)


def on_message(client, userdata, msg):
    try:
        if msg.payload:
            asyncio.run(sort(msg))
        else:
            print("Получено пустое сообщение")
    except Exception as e:
        print({e})


def on_publish(mosq, obj, mid):
    pass


async def start_mqtt_client():
    client = Client()
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect("192.168.1.15", 1883, 60)
    client.subscribe("test", 0)
    client.subscribe("test1", 0)
    client.loop_start()


async def check_inactive_endpoints():
    while True:
        await asyncio.sleep(10)
        current_time = datetime.datetime.now()
        active_endpoints_keys = list(active_v_sn.keys())
        for vir_sn in active_endpoints_keys:
            last_updated_time = active_v_sn[vir_sn]
            if current_time - last_updated_time > datetime.timedelta(seconds=10):
                inactive_entries = ss_main_cell.select().where(ss_main_cell.vir_sn_eid == vir_sn)
                for entry in inactive_entries:
                    move_to_report(entry, reason="inactive")
                    entry.sn = None
                    entry.balance_status = None
                    entry.capacity = None
                    entry.cap_coulo = None
                    entry.cap_percent = None
                    entry.cap_vol = None
                    entry.charge_cap_h = None
                    entry.charge_cap_l = None
                    entry.charge_times = None
                    entry.core_volt = None
                    entry.current_cur = None
                    entry.cycle_times = None
                    entry.design_voltage = None
                    entry.fun_boolean = None
                    entry.healthy = None
                    entry.ochg_state = None
                    entry.odis_state = None
                    entry.over_discharge_times = None
                    entry.pcb_ver = None
                    entry.remaining_cap = None
                    entry.remaining_cap_percent = None
                    entry.sw_ver = None
                    entry.temp_cur1 = None
                    entry.temp_cur2 = None
                    entry.total_capacity = None
                    entry.vid = None
                    entry.voltage_cur = None
                    entry.session_start = None
                    entry.session_end = None
                    entry.time = None
                    entry.status = "Inactive"
                    entry.save()

                del active_v_sn[vir_sn]


if __name__ == '__main__':
    asyncio.run(start_mqtt_client())
    asyncio.run(check_inactive_endpoints())
