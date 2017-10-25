import os, sys, inspect
import_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"connector_client")))
if import_path not in sys.path:
    sys.path.insert(0, import_path)

try:
    from modules.logger import root_logger
    from modules.http_lib import Methods as http
    from modules.device_pool import DevicePool
    from connector.client import Client
    from connector.device import Device
    from smart_meter_serial import SmartMeterSerial
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))
import datetime, json, threading


logger = root_logger.getChild(__name__)


smart_meter = Device('c98b2c1a-ba68', 'iot#40c41048-3910-468f-ae74-7425dde90963', 'Landis+Gyr E350')
smart_meter.addTag('type', 'Smart Meter')
smart_meter.addTag('manufacturer', 'Landis+Gyr')
DevicePool.add(smart_meter)


sm_serial = SmartMeterSerial()


def getReading(source):
    payload = dict()
    while True:
        readings = source.read()
        if readings:
            payload['value'] = float(readings['1.8.0'][0])
            payload['unit'] = readings['1.8.0'][1]
            payload['time'] = datetime.datetime.now().isoformat()
            Client.event(device='c98b2c1a-ba68', service='sepl_get', payload=json.dumps(payload))


if __name__ == '__main__':
    connector_client = Client(device_manager=DevicePool)
    getReading(sm_serial)
