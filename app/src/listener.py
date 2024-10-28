import asyncio
import datetime
import json

import paho.mqtt.publish as publish
import pytz
from paho.mqtt.client import Client

from app.database.models.cabinets import Ss_main_cabinet
from app.database.models.modules import ss_main_cell, ss_main_marked, ss_main_big_battary_list, \
    ss_main_cabinet_settings_for_auto_marking, ss_main_settings_for_settings
from app.database.models.report import Ss_main_report

active_v_sn = {}


def initialize_cells():
    try:
        cells = list(ss_main_cell.select())
        for cell in cells:
            reset_cell_fields(cell)
            cell.save()
        print("Все записи обнулены успешно.")
    except Exception as e:
        print(f"Ошибка при инициализации ячеек: {e}")


def reset_cell_fields(cell):
    """ Reset fields to default values. """
    fields_to_reset = [
        "sn", "balance_status", "capacity", "cap_coulo", "cap_percent",
        "cap_vol", "charge_cap_h", "charge_cap_l", "charge_times",
        "core_volt", "current_cur", "cycle_times", "design_voltage",
        "fun_boolean", "healthy", "ochg_state", "odis_state",
        "over_discharge_times", "pcb_ver", "remaining_cap",
        "remaining_cap_percent", "sw_ver", "temp_cur1", "temp_cur2",
        "total_capacity", "vid", "voltage_cur", "session_start",
        "session_end", "time", "status", "message"
    ]
    for field in fields_to_reset:
        setattr(cell, field, None)
    cell.status = "initialization"


def initialize_active_v_sn():
    try:
        cells = list(ss_main_cell.select())
        for cell in cells:
            vir_sn_eid = cell.vir_sn_eid
            if vir_sn_eid:
                active_v_sn[vir_sn_eid] = datetime.datetime.now()
        print("Словарь активных записей инициализирован успешно.")
    except Exception as e:
        print(f"Ошибка при инициализации active_v_sn: {e}")


def sanitize(value):
    if value and '\x00' in value:
        print(f"Найден нулевой байт в значении: {value}")
        sanitized_value = value.replace('\x00', '')
        if not ss_main_marked.select().where(ss_main_marked.sn == sanitized_value).exists():
            ss_main_marked.create(sn=sanitized_value)
        else:
            existing_entry = ss_main_marked.get(ss_main_marked.sn == sanitized_value)
            existing_entry.is_error = True
            existing_entry.save()
        return sanitized_value
    return value


def extract_year_from_sn(sn):
    if sn[5:7].isdigit():
        return "20" + sn[5:7]
    else:
        print(f"Не удалось извлечь год из серийного номера: {sn}")
        return None


def update_or_add_big_battery_list(sn, cycle_times, stat_id):
    cabinet_setting = ss_main_cabinet_settings_for_auto_marking.get(
        ss_main_cabinet_settings_for_auto_marking.cabinet_id_id == stat_id
    )

    year = extract_year_from_sn(sn)
    if not year:
        print(f"Не удалось обновить запись: неверный серийный номер {sn}")
        return

    existing_entry = ss_main_big_battary_list.select().where(ss_main_big_battary_list.sn == sn).first()

    if existing_entry:
        if existing_entry.cycle_times != cycle_times or existing_entry.year != year:
            print(f"Обновление записи для SN: {sn}")
            existing_entry.year = year
            existing_entry.cycle_times = cycle_times
            existing_entry.is_tired = (int(cycle_times) > cabinet_setting.max_cycle_times)
            existing_entry.save()
        else:
            print(f"Запись для SN: {sn} уже актуальна")
    else:
        print(f"Добавление новой записи для SN: {sn}")
        ss_main_big_battary_list.create(
            sn=sn,
            year=year,
            cycle_times=cycle_times,
            is_tired=(int(cycle_times) > cabinet_setting.max_cycle_times)
        )


def update_entry(existing_entry, stat_id, status_data, en_error, end_id):
    almaty_timezone = pytz.timezone('Asia/Almaty')
    current_time = datetime.datetime.now(almaty_timezone).replace(tzinfo=None)

    cabinet_setting = ss_main_cabinet_settings_for_auto_marking.get(
        ss_main_cabinet_settings_for_auto_marking.cabinet_id_id == stat_id
    )
    print("Получены настройки для шкафа", cabinet_setting.cabinet_id_id.shkaf_id)

    settings_for_settings = ss_main_settings_for_settings.get(ss_main_settings_for_settings.settings_for_id == stat_id)
    print("Получены настройки для блять настроек", settings_for_settings.settings_for_id.settings_for)

    existing_entry.cabinet_id_id = stat_id
    existing_entry.balance_status = status_data.get("BALANCE_STATUS")
    existing_entry.capacity = status_data.get("CAPACITY")
    existing_entry.cap_coulo = status_data.get("CAP_COULO")
    existing_entry.cap_percent = int(status_data.get("CAP_PERCENT", "0")) if status_data.get("CAP_PERCENT") else 0
    existing_entry.cap_vol = status_data.get("CAP_VOL")
    existing_entry.charge_cap_h = status_data.get("CHARGE_CAP_H")
    existing_entry.charge_cap_l = status_data.get("CHARGE_CAP_L")
    existing_entry.charge_times = status_data.get("CHARGE_TIMES")
    existing_entry.core_volt = status_data.get("CORE_VOLT")
    existing_entry.current_cur = status_data.get("CURRENT_CUR")
    existing_entry.cycle_times = status_data.get("CYCLE_TIMES")

    if settings_for_settings.max_cycle_times:
        print("включена проверка циклов")
        if int(status_data.get("CYCLE_TIMES")) >= cabinet_setting.max_cycle_times:
            print(status_data.get("CYCLE_TIMES"), "", cabinet_setting.max_cycle_times)
            existing_entry.is_error = True
            if existing_entry.message:
                if "-Cycle Times " not in existing_entry.message:
                    existing_entry.message += ",-Cycle Times "
            else:
                existing_entry.message = "-Cycle Times "

            print("применены настройки максимального количества циклов")
        else:
            print("количество циклов не превышает максимальное значение")
    else:
        print("проверка циклов отключена")

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

    if settings_for_settings.sw_ver:
        print("включена проверка версии ПО")
        if existing_entry.sw_ver == cabinet_setting.sw_ver:
            print("версия ПО совпадает с разрешенной")
        else:
            print("версия ПО не совпадает с настройками")
            existing_entry.is_error = True
            if existing_entry.message:
                if "-SW version " not in existing_entry.message:
                    existing_entry.message += ",-SW version "
            else:
                existing_entry.message = "-SW version "
    else:
        print("проверка версии ПО отключена")

    existing_entry.temp_cur1 = status_data.get("TEMP_CUR1")
    existing_entry.temp_cur2 = status_data.get("TEMP_CUR2")
    existing_entry.total_capacity = status_data.get("TOTAL_CAPACITY")

    vid_mapping = {
        "4e344007": "JET",
        "4e34300e": "WHOOSH",
        "4e34400d": "YANDEX",
        "4e34400a": "SWING",
        "4e34300c": "VOI"
    }

    existing_entry.vid = next((vid for key, vid in vid_mapping.items() if key in str(status_data.get("VID"))),
                              status_data.get("VID"))

    if settings_for_settings.vid:
        print("включена проверка вендора")
        if existing_entry.vid == cabinet_setting.vid:
            print("вендор cовпадает с настройками")
        else:
            print("вендор не совпадает с настройками")
            existing_entry.is_error = True
            if existing_entry.message:
                if "-Vendor " not in existing_entry.message:
                    existing_entry.message += ",-Vendor "
            else:
                existing_entry.message = "-Vendor "
    else:
        print("проверка вендора отключена")

    existing_entry.voltage_cur = status_data.get("VOLTAGE_CUR")
    existing_entry.time = current_time

    sanitized_sn = sanitize(status_data.get("SN"))
    existing_entry.sn = sanitized_sn

    if sanitized_sn != status_data.get("SN"):
        existing_entry.is_error = True
        if existing_entry.message:
            if "-SN Error" not in existing_entry.message:
                existing_entry.message += ",-SN Error"
        else:
            existing_entry.message = "-SN Error"

    if settings_for_settings.year_of_manufacture:
        print("Проверка года включена")
        if extract_year_from_sn(existing_entry.sn) == cabinet_setting.year_of_manufacture:
            print(extract_year_from_sn(existing_entry.sn), "", cabinet_setting.year_of_manufacture)
            existing_entry.is_error = True
            if existing_entry.message:
                if "-Catch Year" not in existing_entry.message:
                    existing_entry.message += ",-Catch Year"
            else:
                existing_entry.message = "-Catch Year"
            print("Проверка не пройдена")
        else:
            print("Проверка пройдена")
    else:
        print("Проверка года отключена")

    if not existing_entry.session_start:
        existing_entry.session_start = current_time
    existing_entry.session_end = current_time

    if existing_entry.cap_percent >= 91:
        existing_entry.status = "ready"
    elif "4" in str(status_data.get("FUN_BOOLEAN")):
        existing_entry.status = "charging"
    else:
        existing_entry.status = "not_charging"

    #sn = sanitize(status_data.get("SN"))
    #cycle_times = status_data.get("CYCLE_TIMES")
    #update_or_add_big_battery_list(sn, cycle_times, stat_id)

    if en_error == existing_entry.is_error:
        print("статусы ошибок совпадают")
    elif en_error == False and existing_entry.is_error == True:
        print("слот фолс я тру")
        json_data = {
            "Type": "cmd",
            "StationID": int(stat_id),
            "EndpointID": int(end_id),
            "CMD": int(1),
            "SN": sanitize(status_data.get("SN"))
        }
        publish.single("test/back", json.dumps(json_data), hostname="192.168.1.15")
    elif en_error == True and existing_entry.is_error == False:
        print("слот тру я фолс")
        json_data = {
            "Type": "cmd",
            "StationID": int(stat_id),
            "EndpointID": int(end_id),
            "CMD": int(0),
            "SN": sanitize(status_data.get("SN"))
        }
        publish.single("test/back", json.dumps(json_data), hostname="192.168.1.15")
    else:
        print("ну хз выключи компьютер")

    existing_entry.save()
    print(f"Информация для {existing_entry.vir_sn_eid} обновлена.")


def move_to_report(existing_entry, reason):
    import datetime

    almaty_timezone = pytz.timezone('Asia/Almaty')
    current_time_with_tz = datetime.datetime.now(almaty_timezone)
    current_time = current_time_with_tz.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Время: {current_time}")

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
        time=current_time,
        reason=reason,
        city=find_city_name(existing_entry.cabinet_id_id.city.city_name),
        zone=find_zone_name(existing_entry.cabinet_id_id.zone.zone_name)
    )
    print(f"Перемещена строка с Endpoint ID {existing_entry.vir_sn_eid} в отчет из-за {reason}.")


def find_city_name(city_name):
    cabinet = Ss_main_cabinet.get(Ss_main_cabinet.city == city_name)
    return cabinet.city.city_name


def find_zone_name(zone_name):
    cabinet = Ss_main_cabinet.get(Ss_main_cabinet.zone == zone_name)
    return cabinet.zone.zone_name


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
    topic = msg.topic
    print("получено сообщение с топика", topic)

    if message_type == 'Ping' or message_type == 'Report':

        v_end_id = data.get("EndpointID")
        v_stat_id = data.get("StationID")
        end_id = data.get("EndpointID")
        stat_id = data.get("StationID")
        delimiter = "-"
        vir_sn = str(v_stat_id) + str(delimiter) + str(v_end_id)

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
                existing_entry.is_error = False
                existing_entry.message = None
                existing_entry.save()
                print("Обнулены поля существующей записи.")
            else:
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
                existing_entry.is_error = False
                existing_entry.message = None
                existing_entry.save()
        else:
            create_new_entry(end_id, stat_id, status="empty", vir_sn_eid=vir_sn)
        return

    if message_type == 'Status':
        status_on_error = data.get("Status", {}).get("onError")
        en_error = status_on_error.lower() == "true" if isinstance(status_on_error, str) else bool(status_on_error)
        v_end_id = data.get("EndpointID")
        v_stat_id = data.get("StationID")
        end_id = data.get("EndpointID")
        stat_id = data.get("StationID")
        delimiter = "-"
        vir_sn = str(v_stat_id) + str(delimiter) + str(v_end_id)

        sn = data.get("Status", {}).get("SN")
        existing_entry = ss_main_cell.select().where(ss_main_cell.vir_sn_eid == vir_sn).first()

        if existing_entry:
            update_entry(existing_entry, stat_id, data["Status"], en_error, end_id)
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


def on_publish(mosq, obj, mid, is_error_status):
    pass


async def start_mqtt_client():
    client = Client()
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect("192.168.1.15", 1883, 60)
    client.subscribe("test", 0)
    client.subscribe("test/back", 0)
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
                    entry.is_error = False
                    entry.status = "Inactive"
                    entry.message = None
                    entry.save()

                del active_v_sn[vir_sn]


if __name__ == '__main__':
    initialize_cells()
    initialize_active_v_sn()
    asyncio.run(start_mqtt_client())
    asyncio.run(check_inactive_endpoints())
