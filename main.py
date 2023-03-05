import json
import os
import time
import requests
from dotenv import load_dotenv
import logging
from mqtt import MQTTClient
from QRScan import main as QRScan
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
gpio = int(f"{os.getenv('GPIO')}")
GPIO.setup(gpio, GPIO.IN)

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

def checkQR(data):
    result = requests.post(
        f"{os.getenv('API')}/QRCode/CheckQRCode",
        headers={
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        },
        json={
        "qrCodeContent": data
        }
    )

    print(result.json())

if __name__ == "__main__":
    if devicesList == []:
        getIndoorDevices("as")
    
    print(topics)
    
    thisDevice = MQTTClient(clientID)
    thisDevice.connect()
    thisDevice.subscribe(topics)
    thisDevice.client.loop_start()
    logging.info("The device started!")

    while True:
        if GPIO.input(gpio):
            logging.info("Nearing object detected. Scanning for QR code ...")
            data = QRScan()
            result = data["data"]
            logging.info(f"Fetched data {result}. Checking data ...")
            checkQR(result)
'''
INFO:root:Fetched data {\"Id\":11,\"ApartmentCode\":\"I5-2609\"}. Checking data ...
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 65.108.79.164:7200
DEBUG:urllib3.connectionpool:http://65.108.79.164:7200 "POST /api/services/app/QRCode/CheckQRCode HTTP/1.1" 200 None
{'message': 'Exception !', 'error': "Newtonsoft.Json.JsonReaderException: Invalid property identifier character: \\. Path '', line 1, position 1.\n   at Newtonsoft.Json.JsonTextReader.ParseProperty()\n   at Newtonsoft.Json.JsonTextReader.ParseObject()\n   at Newtonsoft.Json.JsonReader.ReadAndAssert()\n   at Newtonsoft.Json.Serialization.JsonSerializerInternalReader.CreateObject(JsonReader reader, Type objectType, JsonContract contract, JsonProperty member, JsonContainerContract containerContract, JsonProperty containerMember, Object existingValue)\n   at Newtonsoft.Json.Serialization.JsonSerializerInternalReader.CreateValueInternal(JsonReader reader, Type objectType, JsonContract contract, JsonProperty member, JsonContainerContract containerContract, JsonProperty containerMember, Object existingValue)\n   at Newtonsoft.Json.Serialization.JsonSerializerInternalReader.Deserialize(JsonReader reader, Type objectType, Boolean checkAdditionalContent)\n   at Newtonsoft.Json.JsonSerializer.DeserializeInternal(JsonReader reader, Type objectType)\n   at Newtonsoft.Json.JsonSerializer.Deserialize(JsonReader reader, Type objectType)\n   at Newtonsoft.Json.JsonConvert.DeserializeObject(String value, Type type, JsonSerializerSettings settings)\n   at Newtonsoft.Json.JsonConvert.DeserializeObject[T](String value, JsonSerializerSettings settings)\n   at Newtonsoft.Json.JsonConvert.DeserializeObject[T](String value)\n   at Project.Controllers.QRCodeController.CheckQRCOdeAsync(CheckQRCodeDto input) in /src/Project.Web.API/Controllers/QRCodeController.cs:line 107", 'success': False, 'data': None, 'totalRecords': None, 'result_Code': None}
'''
