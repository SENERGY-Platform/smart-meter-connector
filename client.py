"""
   Copyright 2018 SEPL Team

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

try:
    from connector_client.modules.http_lib import Methods as http
    from connector_client.modules.device_pool import DevicePool
    from connector_client.client import Client
    from connector_client.device import Device
    from configuration import SM_ID, SM_NAME, SM_MANUFACTURER, SM_TYPE, SEPL_DEVICE_TYPE, SEPL_SERVICE
    from smart_meter_serial import SmartMeterSerial
    from logger import root_logger
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))
import datetime, json


logger = root_logger.getChild(__name__)


smart_meter = Device(SM_ID, SEPL_DEVICE_TYPE, SM_NAME)
if SM_TYPE:
    smart_meter.addTag('type', SM_TYPE)
if SM_MANUFACTURER:
    smart_meter.addTag('manufacturer', SM_MANUFACTURER)
DevicePool.add(smart_meter)


sm_serial = SmartMeterSerial()


def getReading(source):
    payload = dict()
    while True:
        readings = source.read()
        if readings:
            payload['value'] = float(readings['1.8.0'][0])
            payload['unit'] = readings['1.8.0'][1]
            payload['time'] = '{}Z'.format(datetime.datetime.utcnow().isoformat())
            Client.event(device=SM_ID, service=SEPL_SERVICE, data=json.dumps(payload))


if __name__ == '__main__':
    connector_client = Client(device_manager=DevicePool)
    getReading(sm_serial)
