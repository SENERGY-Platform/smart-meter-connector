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
