if __name__ == '__main__':
    exit('Please use "client.py"')

import os, configparser

conf_path = os.getcwd()
conf_file = 'sm.conf'

config = configparser.ConfigParser()


if not os.path.isfile(os.path.join(conf_path, conf_file)):
    print('No config file found')
    config['SMART_METER'] = {
        'id': '',
        'name': '',
        'manufacturer': '',
        'type': ''
    }
    config['SEPL'] = {
        'device_type': '',
        'device_service': ''
    }
    with open(os.path.join(conf_path, conf_file), 'w') as cf:
        config.write(cf)
    exit("Created blank config file at '{}'".format(conf_path))


try:
    config.read(os.path.join(conf_path, conf_file))
except Exception as ex:
    exit(ex)


SM_ID = config['SMART_METER']['id']
SM_NAME = config['SMART_METER']['name']
SM_MANUFACTURER = config['SMART_METER']['manufacturer']
SM_TYPE = config['SMART_METER']['type']
SEPL_DEVICE_TYPE = config['SEPL']['device_type']
SEPL_SERVICE = config['SEPL']['device_service']


if not SM_ID or not SM_NAME:
    exit('Please provide a smart meter ID and name')

if not SEPL_DEVICE_TYPE or not SEPL_SERVICE:
    exit('Please provide a SEPL device type and service')