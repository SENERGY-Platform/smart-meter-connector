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

__all__ = ('ReadingsEmitter',)


from .logger import root_logger
from .serial_adapter import ReadError
from threading import Thread
from time import sleep
import cc_lib, json

logger = root_logger.getChild(__name__)


class ReadingsEmitter(Thread):

    def __init__(self, device: cc_lib.types.Device, client: cc_lib.client.Client):
        super().__init__(name="{}-{}".format(__class__.__name__, device.id), daemon=True)
        self.__device = device
        self.__client = client

    def run(self) -> None:
        logger.info("starting reader for '{}'".format(self.__device.id))
        self.__client.connectDevice(self.__device, asynchronous=True)
        msg = cc_lib.client.message.Message(str())
        srv = "getMeasurements"
        count = 0
        while True:
            try:
                payload = self.__device.getService(srv)
                msg.data = json.dumps(payload)
                envelope = cc_lib.client.message.EventEnvelope(
                    self.__device,
                    srv,
                    msg
                )
                self.__client.emmitEvent(envelope, asynchronous=True)
            except ReadError:
                count += 1
                if count > 3:
                    self.__device.adapter = None
                    break
                sleep(1)
        self.__client.disconnectDevice(self.__device, asynchronous=True)
        logger.warning("reader for '{}' quit".format(self.__device.id))
