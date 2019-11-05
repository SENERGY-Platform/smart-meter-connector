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


__all__ = ('LandisGyrE350', 'device_type_map')


from ..configuration import config
from .service import GetMeasurements
import cc_lib


class LandisGyrE350(cc_lib.types.Device):
    device_type_id = config.Senergy.dt_sm
    services = (GetMeasurements, )

    def __init__(self, id: str, adapter: None):
        self.id = id
        self.name = "Landis+Gyr E350 ({})".format(id)
        self.adapter = adapter

    def getService(self, srv_handler: str):
        service = super().getService(srv_handler)
        return service.task(self.adapter)


device_type_map = {
    "LGZ0ZMF100AC": LandisGyrE350,
    "LGZ1ZMF100AC": LandisGyrE350,
    "LGZ2ZMF100AC": LandisGyrE350,
    "LGZ3ZMF100AC": LandisGyrE350,
    "LGZ4ZMF100AC": LandisGyrE350
}