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

__all__ = ('config', )


from simple_conf import configuration, section
from os import getcwd, makedirs
from os.path import exists as path_exists

user_dir = '{}/storage'.format(getcwd())


@configuration
class SMConf:

    @section
    class Serial:
        base_path = None
        port_filter = None

    @section
    class Senergy:
        dt_sm = None

    @section
    class Logger:
        level = "info"

    @section
    class RuntimeEnv:
        max_start_delay = 30


if not path_exists(user_dir):
    makedirs(user_dir)

config = SMConf('sm.conf', user_dir)


if not all((config.Serial.base_path, )):
    exit('Please provide Smart Meter information')

if not all((config.Senergy.dt_sm, )):
    exit('Please provide a SENERGY device and service types')
