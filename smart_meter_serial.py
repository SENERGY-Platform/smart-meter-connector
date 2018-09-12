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

if __name__ == '__main__':
    exit('Please use "client.py"')

try:
    from logger import root_logger
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))
import serial

logger = root_logger.getChild(__name__)


class SmartMeterSerial:
    """
    Access a smart meter serial port.

    !!! Customized for Landis & Gyr E350 !!!

    http://www.mayor.de/lian98/doc.de/html/g_iec62056_struct.htm
    http://www.december.com/html/spec/ascii.html
    https://pyserial.readthedocs.io/en/latest/
    http://www.baer-gmbh.com/downl/MBus-Komm-Modul-Beschreibung.pdf
    https://wiki.volkszaehler.org/hardware/channels/meters/power/edl-ehz/e350
    """
    init_telegram = '\x2f\x3f\x21\x0d\x0a'.encode()     # '/?! CR LF'
    ack_telegram = '\x06\x30\x30\x30\x0d\x0a'.encode()  # 'ACK 000 CR LF'

    def __init__(self):
        self.serial_con = serial.Serial()
        self.serial_con.port = '/dev/ttyUSB0'
        self.serial_con.baudrate = 300
        self.serial_con.parity = serial.PARITY_EVEN
        self.serial_con.stopbits = serial.STOPBITS_ONE
        self.serial_con.bytesize = serial.SEVENBITS
        self.serial_con.timeout = 1
        logger.debug(self.serial_con)

    def read(self):
        try:
            # open serial port
            self.serial_con.open()

            # write initial telegram
            self.serial_con.write(__class__.init_telegram)

            # read identification telegram
            ident_telegram = self.serial_con.readall()
            if not ident_telegram or not 'LGZ4ZMF100AC.M23' in ident_telegram.decode():
                logger.error("missing or malformed identification telegram: {}".format(ident_telegram))
                self.serial_con.close()
                return None
            logger.debug(ident_telegram)

            # write acknowledgement telegram
            self.serial_con.write(__class__.ack_telegram)

            # read data telegram
            data_telegram = self.serial_con.readall()
            if not data_telegram or len(data_telegram.decode()) < 20:
                logger.error("missing or malformed data telegram: {}".format(data_telegram))
                self.serial_con.close()
                return None
            logger.debug(data_telegram)

            # close serial port
            self.serial_con.close()

            return self._mapReadings(data_telegram.decode())
        except Exception as ex:
            logger.error(ex)

    def _mapReadings(self, data):
        readings = dict()
        readings_list = data.split('\r\n')
        for reading in readings_list:
            if '(' in reading:
                key, value = reading.split('(')
                if '*' in value:
                    value, unit = value.split('*')
                    unit = unit.replace(')', '')
                else:
                    value = value.replace(')', '')
                    unit = None
                readings[key] = (value, unit)
        return readings
