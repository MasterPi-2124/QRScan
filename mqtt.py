import paho.mqtt.client as mqtt_client
from dotenv import load_dotenv
import os
import logging
import time

load_dotenv()

class MQTTClient:
    def __init__(self, clientID):
        self.broker = f"{os.getenv('BROKER')}"
        self.port = int(f"{os.getenv('PORT')}")
        self.username = f"{os.getenv('USERNAME')}"
        self.password = f"{os.getenv('PASSWORD')}"
        self.clientID = clientID
        
    def connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logging.info(f"Connected to broker {self.broker}:{self.port} as user {self.username}")
            else:
                logging.error(f"Failed to connect to broker {self.broker}:{self.port}, return code {rc}.")
                
        # Set Connecting Client ID
        client = mqtt_client.Client(self.clientID)
        client.username_pw_set(self.username, self.password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        self.client = client
        
    def subscribe(self, topic):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        self.client.subscribe(topic)
        self.client.on_message = on_message
    
    def publish(self, message, topic):
        res = self.client.publish(topic = topic[0], payload = message, qos = topic[1])
        
        if res[0] == 0:
            logging.info(f"Sent data to topic {topic}.")
        else: 
            logging.error(f"Failed to send data to {topic}.")
    
    def disconnect(self):
        def on_disconnect(client, userdata, rc):
            self.client.loop_stop()
            
        self.client.disconnect()
        self.client.on_disconnect = on_disconnect
        logging.info(f"Client disconnected from broker {self.broker}:{self.port}")
    
    def call(self, topic):
        res = self.client.publish(topic = topic[0], payload = str({
            "MQTT_STATUS_CODE": 1,
            "date": time.ctime()
        }), qos = topic[1])
        
        if res[0] == 0:
            logging.info(f"Sent data to topic {topic}.")
        else: 
            logging.error(f"Failed to send data to {topic}.")