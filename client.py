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


from sm_manager import root_logger, DeviceManager, SerialMonitor
from time import sleep
import json
import cc_lib


logger = root_logger.getChild(__name__)


device_manager = DeviceManager()


def on_connect(client: cc_lib.client.Client):
    devices = device_manager.devices.values()
    for device in devices:
        try:
            if device.adapter:
                client.connectDevice(device, asynchronous=True)
        except cc_lib.client.DeviceConnectError:
            pass


connector_client = cc_lib.client.Client()
connector_client.setConnectClbk(on_connect)

serial_monitor = SerialMonitor(device_manager, connector_client)

def pushReadings():
    msg = cc_lib.client.message.Message(str())
    srv = "getMeasurements"
    delay = True
    while True:
        delay = True
        for device in device_manager.devices.values():
            if device.adapter:
                delay = False
                payload = device.getService(srv)
                if payload:
                    msg.data = json.dumps(payload)
                    envelope = cc_lib.client.message.Envelope(
                        device,
                        srv,
                        msg
                    )
                    connector_client.emmitEvent(envelope, asynchronous=True)
        if delay:
            sleep(5)


if __name__ == '__main__':
    while True:
        try:
            connector_client.initHub()
            break
        except cc_lib.client.HubInitializationError:
            sleep(10)
    connector_client.connect(reconnect=True)
    serial_monitor.start()
    pushReadings()
