try:
    from connector_client.modules.http_lib import Methods as http
    from connector_client.modules.device_pool import DevicePool
    from connector_client.client import Client
    from connector_client.device import Device
    from smart_meter_serial import SmartMeterSerial
    from logger import root_logger
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))
import datetime, json


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
            payload['time'] = datetime.datetime.utcnow().isoformat()
            Client.event(device='c98b2c1a-ba68', service='reading', data=json.dumps(payload))


if __name__ == '__main__':
    connector_client = Client(device_manager=DevicePool)
    getReading(sm_serial)
