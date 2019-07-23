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


__all__ = ('GetMeasurements', )


from ..configuration import config
from datetime import datetime
import cc_lib


class GetMeasurements(cc_lib.types.SensorService):
    uri = config.Senergy.st_sm
    name = "Push Reading"
    description = "Push current reading from a smart meter."

    @staticmethod
    def task(source):
        reading = source.read()
        return {
            "OBIS_1_8_0": {
                "value": float(reading["1.8.0"][0]),
                "unit": reading["1.8.0"][1]
            },
            "OBIS_16_7": {
                "value": float(reading["16.7"][0]),
                "unit": reading["16.7"][1]
            },
            "time": '{}Z'.format(datetime.utcnow().isoformat())
        }
