import json
import time
import paho.mqtt.client as mqtt
from peewee import *

try:
    db = PostgresqlDatabase('testik6', user='bogdanafter', password='bogdanafter', host='192.168.1.206', port=5432)
    print(":)")
except Exception as e:
    print(":(")
    print("Ошибка подключения:", e)
    exit(1)


class BaseModel(Model):
    class Meta:
        database = db


class Ss_main_cabinet(BaseModel):
    shkaf_id = CharField(primary_key=True)


class Ss_main_cell(BaseModel):
    endpointid = CharField(column_name='endpointid')
    cabinet_id_id = ForeignKeyField(Ss_main_cabinet, field=Ss_main_cabinet.shkaf_id, related_name='shkaf_id',
                                    on_delete='CASCADE')
    sn = CharField(null=True, column_name='sn')

    class Meta:
        table_name = 'ss_main_cell'


def publish_message(json_data):
    client = mqtt.Client()
    client.connect("192.168.1.15", 1883, 60)
    client.publish("test/back", json_data)
    client.disconnect()


def main():
    print("Скрипт запущен")

    cabinet_id = input("Введите CabinetID: ")
    endpoint_id = input("Введите EndpointID: ")
    cmd_number = input("Введите номер команды (cmd): ")

    record = Ss_main_cell.select().where(
        (Ss_main_cell.cabinet_id_id == cabinet_id) &
        (Ss_main_cell.endpointid == endpoint_id)
    ).first()

    if record:
        json_data = {
            "Type": "cmd",
            "StationID": int(record.cabinet_id_id.shkaf_id),
            "EndpointID": int(record.endpointid),
            "CMD": int(cmd_number),
            "SN": record.sn
        }

        json_str = json.dumps(json_data)

        while True:
            try:
                publish_message(json_str)
                print(json_str)
            except Exception as e:
                print("Произошла ошибка:", e)

            time.sleep(3)
    else:
        print("Запись не найдена. Пожалуйста, попробуйте снова.")


if __name__ == '__main__':
    main()
