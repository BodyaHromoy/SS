import paho.mqtt.client as mqtt
import threading
import time


BROKER = '192.168.1.15'
PORT = 1883
TOPIC_SUB = 'test/topic/pub'
TOPIC_PUB = 'test/topic/pub'
CLIENT_ID = 'python-mqtt-client'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Подключение к брокеру успешно!")
        client.subscribe(TOPIC_SUB)
    else:
        print(f"Ошибка подключения, код: {rc}")


def on_message(client, userdata, msg):
    print(f"Получено сообщение: {msg.payload.decode()} из топика: {msg.topic}")


def publish(client):
        message = f"Сообщение отправлено в {time.ctime()}"
        client.publish(TOPIC_PUB, message)
        print(f"Отправлено сообщение: {message}")
        time.sleep(5)


def run():
    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    publish_thread = threading.Thread(target=publish, args=(client,))
    publish_thread.start()
    client.loop_forever()


if __name__ == '__main__':
    run()
