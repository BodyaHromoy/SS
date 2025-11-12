import json
import paho.mqtt.client as mqtt
from datetime import datetime
import time
import random
import string

broker = "185.22.67.4"
port = 1883
topic = "test1"


def generate_sn():
    letters = string.ascii_uppercase
    first_part = ''.join(random.choices(letters, k=5))
    middle_number = str(random.randint(18, 25))
    last_part = ''.join(random.choices(letters, k=5))
    return first_part + middle_number + last_part


def create_status_message():
    return json.dumps({
        "EndpointID": random.randint(1, 99),
        "StationID": 99,
        "Status": {
            "BALANCE_STATUS": "0",
            "CAPACITY": "15300",
            "CAP_COULO": "9192",
            "CAP_PERCENT": "66",
            "CAP_VOL": "9091",
            "CHARGE_CAP_H": "65535",
            "CHARGE_CAP_L": "65535",
            "CHARGE_TIMES": "94",
            "CORE_VOLT": [
                "3.813", "3.804", "3.81", "3.816", "3.808", "3.807",
                "3.819", "3.815", "3.81", "3.815", "-0.001", "-0.001",
                "-0.001", "-0.001", "-0.001", "-0.001"
            ],
            "CURRENT_CUR": "-4.93",
            "CYCLE_TIMES": "68",
            "DESIGN_VOLTAGE": "36.5",
            "FUN_BOOLEAN": "0x41",
            "HEALTHY": "98",
            "OCHG_STATE": "0xffffffffffffffff",
            "ODIS_STATE": "0xffffffffffffffff",
            "OVER_DISCHARGE_TIMES": "65535",
            "PCB_VER": "2",
            "REMAINING_CAP": "10155",
            "REMAINING_CAP_PERCENT": "66",
            "SN": generate_sn(),
            "SW_VER": "TEST",
            "TEMP_CUR1": "27",
            "TEMP_CUR2": "51",
            "TOTAL_CAPACITY": "15300",
            "VID": "JET",
            "VOLTAGE_CUR": "38.1",
            "time": datetime.now().isoformat()
        },
        "Type": "Status"
    })


def send_message(client, topic, message):
    client.publish(topic, message)
    print(f"Отправлено сообщение в топик {topic}: {message}")


if __name__ == "__main__":
    client = mqtt.Client()

    try:
        client.connect(broker, port)

        while True:
            status_message = create_status_message()
            send_message(client, topic, status_message)
            time.sleep(1)

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client.disconnect()
