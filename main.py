import os
import time
import requests
from dotenv import load_dotenv
import logging
from mqtt import MQTTClient
from QRScan import main as QRScan

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

devicesList = topics = []
clientID = ""

def getIndoorDevices(ID):
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
        logging.info(f"Found {len(devicesList)} devices. Found these topics: {topics}")

if __name__ == "__main__":
    if devicesList == []:
        getIndoorDevices("as")
    
    print(topics)
    
    thisDevice = MQTTClient(clientID)
    thisDevice.connect()
    thisDevice.subscribe(topics)
    thisDevice.client.loop_start()
    while True:
        logging.info("The device started!")
