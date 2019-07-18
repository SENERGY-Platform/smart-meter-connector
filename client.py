"""
   Copyright 2019 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


from configuration import config
from smart_meter_serial import SmartMeterSerial
from logger import root_logger
from time import sleep
import datetime
import json
import cc_lib


logger = root_logger.getChild(__name__)


class GetMeasurements(cc_lib.types.SensorService):
    uri = config.Senergy.st_sm
    name = "Push Reading"
    description = "Push current reading from a smart meter"

    @staticmethod
    def task(source):
        reading = source.read()
        if reading:
            return {
                "OBIS_1_8_0": {
                    "value": float(reading["1.8.0"][0]),
                    "unit": reading["1.8.0"][1]
                },
                "OBIS_16_7": {
                    "value": float(reading["16.7"][0]),
                    "unit": reading["16.7"][1]
                },
                "time": '{}Z'.format(datetime.datetime.utcnow().isoformat())
            }


class GenericSmartMeter(cc_lib.types.Device):
    uri = config.Senergy.dt_sm
    description = "Device type for Smart Meters"
    services = {
        "getMeasurements": GetMeasurements
    }

    def __init__(self, id: str, name: str, manufacturer: str, source):
        self.id = id
        self.name = name
        self.addTag('manufacturer', manufacturer)
        self.source = source

    def getService(self, srv_handler: str):
        service = super().getService(srv_handler)
        return service.task(self.source)


devices = list()

devices.append(
    GenericSmartMeter(config.SmartMeter.id,config.SmartMeter.name,config.SmartMeter.manufacturer,SmartMeterSerial())
)


def on_connect(client: cc_lib.client.Client):
    try:
        client.syncHub(devices)
    except cc_lib.client._exception.HubSyncDeviceError:
        for device in devices:
            client.addDevice(device, asynchronous=True)
        client.syncHub(devices)
    for device in devices:
        try:
            client.connectDevice(device, asynchronous=True)
        except cc_lib.client.DeviceConnectError:
            pass


connector_client = cc_lib.client.Client()
connector_client.setConnectClbk(on_connect)


def pushReadings():
    msg = cc_lib.client.message.Message(str())
    srv = "getMeasurements"
    while True:
        for device in devices:
            payload = device.getService(srv)
            if payload:
                msg.data = json.dumps(payload)
                envelope = cc_lib.client.message.Envelope(
                    device,
                    srv,
                    msg
                )
                connector_client.emmitEvent(envelope, asynchronous=True)
        sleep(5)


if __name__ == '__main__':
    while True:
        try:
            connector_client.initHub()
            break
        except cc_lib.client.HubInitializationError:
            sleep(10)
    connector_client.connect(reconnect=True)
    pushReadings()
