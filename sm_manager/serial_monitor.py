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

__all__ = ('SerialMonitor', )


from .logger import root_logger
from .configuration import config
from .serial_adapter import SerialAdapter, ReadError
from .types import device_type_map
from .device_manager import DeviceManager
from .readings_emitter import ReadingsEmitter
from threading import Thread
from time import sleep
import os, cc_lib


logger = root_logger.getChild(__name__)


class SerialMonitor(Thread):
    def __init__(self, device_manager: DeviceManager, client: cc_lib.client.Client):
        super().__init__(name="SerialMonitor", daemon=True)
        self.__device_manager = device_manager
        self.__client = client

    def __getPorts(self):
        ports = list()
        for port in os.listdir(config.Serial.base_path):
            if os.path.isabs(os.path.join(config.Serial.base_path, port)):
                if config.Serial.port_filter:
                    if config.Serial.port_filter in port:
                        ports.append(os.path.join(config.Serial.base_path, port))
                else:
                    ports.append(os.path.join(config.Serial.base_path, port))
        return ports

    def __probePorts(self, ports):
        smart_meters = list()
        for port in ports:
            try:
                srl_adptr = SerialAdapter(port)
                mfr_id, sm_id = srl_adptr.identify()
                if mfr_id and sm_id:
                    logger.info("found smart meter '{}' with id '{}' on '{}'".format(mfr_id, sm_id, port))
                    smart_meters.append((sm_id, mfr_id, srl_adptr))
            except ReadError:
                pass
        return smart_meters

    def __addDevices(self, smart_meters):
        futures = list()
        for sm_id, mfr_id, srl_adptr in smart_meters:
            try:
                device = self.__device_manager.get(sm_id)
                device.adapter = srl_adptr
            except KeyError:
                device = device_type_map[mfr_id](sm_id, srl_adptr)
            futures.append((device, mfr_id, self.__client.addDevice(device, asynchronous=True)))
        for device, mfr_id, future in futures:
            future.wait()
            try:
                future.result()
                self.__device_manager.add(device, mfr_id)
                emitter = ReadingsEmitter(device, self.__client)
                emitter.start()
            except (cc_lib.client.DeviceAddError, cc_lib.client.DeviceUpdateError):
                pass

    def run(self) -> None:
        while True:
            ports = self.__getPorts()
            logger.debug("available ports: {}".format(ports))
            active_ports = [device.adapter.source for device in self.__device_manager.devices.values() if device.adapter and type(device.adapter) is SerialAdapter]
            logger.debug("active ports {}".format(active_ports))
            inactive_ports = list(set(ports) - set(active_ports))
            logger.debug("inactive ports {}".format(inactive_ports))
            smart_meters = self.__probePorts(inactive_ports)
            self.__addDevices(smart_meters)
            if smart_meters:
                try:
                    self.__client.syncHub(list(self.__device_manager.devices.values()))
                except cc_lib.client.HubError:
                    pass
            sleep(10)
