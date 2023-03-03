from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
import os

load_dotenv()

def connect_mqtt(client_id, username, password, broker, port):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def initTopic(apartmentID):
    broker = os.getenv('BROKER')
    port = os.getenv('PORT')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    topic = f"{apartmentID}@outdoor"
    client_id = f"{apartmentID}"
    client = connect_mqtt(client_id, username, password, broker, port)
