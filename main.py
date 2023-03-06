import os
import requests
from dotenv import load_dotenv
import logging
from mqtt import MQTTClient
from QRScan import main as QRScan
import RPi.GPIO as GPIO
import time

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
gpio = int(f"{os.getenv('GPIO')}")
GPIO.setup(gpio, GPIO.IN)

devicesList = topics = []
clientID = ""

def getIndoorDevices():
    global devicesList, topics, clientID
    devicesList = requests.get(
        f"{os.getenv('API')}/IndoorDevice/GetIndoorDevices",
        headers={
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        }
    )
    
    devicesList = devicesList.json()['data']
    clientID = devicesList[0]['apartmentCode'] + "@outdoor"
    if len(devicesList) == 0:
        logging.error("No Indoor devices found! This device requires at least one indoor device to work.")
        exit(1)
    else:
        for topic in devicesList:
            topics.append((topic['apartmentCode'], 1))
        topics.append(("opendoor", 1))
        logging.info(f"Found {len(devicesList)} devices. Found these topics: {topics}")

def saveHistory(result, MQTT_STATUS):
    requests.post(f"{os.getenv('API')}/AccessHistory/SaveAccessHistory",
                        headers={
            "accept": "text/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        },
        json={
        "apartmentCode": result["data"]["apartmentCode"],
        "visitorName": result["data"]["visitorName"],
        "mqttType": MQTT_STATUS
        })
    
    
def checkQR(data):
    s = ""
    for i in data:
        if i != "\\":
            s = s + i
    print(s)

    result = requests.post(
        f"{os.getenv('API')}/QRCode/CheckQRCode",
        headers={
            "accept": "text/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        },
        json={
        "qrCodeContent": s
        }
    )
    result = result.json()

    if result["message"] == "Mã QR code hợp lệ":
        saveHistory(result, 5)
        thisDevice.publish("3", ("opendoor", 1))
        return True
    else:
        saveHistory(result, 6)
        return False

if __name__ == "__main__":
    if devicesList == []:
        getIndoorDevices()
    
    thisDevice = MQTTClient(clientID)
    thisDevice.connect()
    thisDevice.subscribe(topics)
    thisDevice.client.loop_start()
    logging.info("The device started!")

    while True:
        # if GPIO.input(gpio):
        #     logging.info("Nearing object detected. Scanning for QR code ...")
        #     data = QRScan()
        #     result = data["data"]
        #     logging.info(f"Fetched data {result}. Checking data ...")
        #     if checkQR(result):
        #         for topic in topics:
        #             thisDevice.publish(message=str({
        #                 "MQTT_STATUS": 5,
        #                 "date": data["date"]
        #             }),
        #             topic = topic)
        #     else:
        #         for topic in topics:
        #             thisDevice.publish(message=str({
        #                 "MQTT_STATUS": 6,
        #                 "date": data["date"]
        #             }),
        #             topic = topic)
        time.sleep(5)
        for topic in topics:
            thisDevice.call(topic)
        time.sleep(600)
