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


from .logger import root_logger
from time import sleep
import serial

logger = root_logger.getChild(__name__)


class SmartMeterSerial:
    init_telegram = '\x2f\x3f\x21\x0d\x0a'.encode()     # '/?! CR LF'
    ack_telegram = '\x06\x30\x35\x30\x0d\x0a'.encode()  # 'ACK 050 CR LF'

    def __init__(self, port):
        self.serial_con = serial.Serial()
        self.serial_con.port = port
        self.serial_con.parity = serial.PARITY_EVEN
        self.serial_con.stopbits = serial.STOPBITS_ONE
        self.serial_con.bytesize = serial.SEVENBITS
        self.serial_con.timeout = 1

    def __read(self):
        try:
            self.serial_con.baudrate = 300

            # open serial port
            self.serial_con.open()

            # write initial telegram
            self.serial_con.write(__class__.init_telegram)

            # read identification telegram
            ident_telegram = self.serial_con.readall()
            if not ident_telegram: #or not self.mfr_ident in ident_telegram.decode():
                logger.error("missing identification telegram: {}".format(ident_telegram))
                self.serial_con.close()
                return None, None
            logger.debug(ident_telegram)

            # write acknowledgement telegram
            self.serial_con.write(__class__.ack_telegram)

            # change baudrate
            sleep(0.5)
            self.serial_con.baudrate = 9600

            # read data telegram
            data_telegram = self.serial_con.readall()
            if not data_telegram or len(data_telegram.decode()) < 20:
                logger.error("missing or malformed data telegram: {}".format(data_telegram))
                self.serial_con.close()
                return None, None
            logger.debug(data_telegram)

            # close serial port
            self.serial_con.close()

            return ident_telegram.decode(), data_telegram.decode()
        except Exception as ex:
            logger.error(ex)

    def read(self):
        _, dt = self.__read()
        if dt:
            return self.__parseDataTelegram(dt)

    def identify(self):
        mfr_id, dt = self.__read()
        if mfr_id and dt:
            mfr_id = mfr_id.replace("\r", "")
            mfr_id = mfr_id.replace("\n", "")
            mfr_id = mfr_id.replace("/", "")
            mfr_id = mfr_id.split(".")
            if type(mfr_id) is list:
                mfr_id = mfr_id[0]
            dt = self.__parseDataTelegram(dt)
            meter_ids = list()
            for m_id, val in dt.items():
                if m_id in ("C.1.0", "C.1.1", "0.0") and not str(val[0]).isspace() and not str(val[0]) in meter_ids:
                    meter_ids.append(str(val[0]))
            meter_ids.sort()
            return mfr_id, "".join(meter_ids)
        return None, None

    def __parseDataTelegram(self, data):
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
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                readings[key] = (value, unit)
        return readings
