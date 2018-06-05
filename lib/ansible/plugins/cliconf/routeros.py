#
# (c) 2017 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import json

from itertools import chain

from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class Cliconf(CliconfBase):

    def get_device_info(self):
        display.vvvv('get_device_info')
        device_info = {}

        device_info['network_os'] = 'RouterOS'

        resource = self.get(b'/system resource print')
        data_a = to_text(resource, errors='surrogate_or_strict').strip()
        display.vvvv("result: '%s'" % str(data_a))
        match = re.search(r'version: (\S+)', data_a)
        if match:
            display.vvvv("network_os_version: '%s'" % match.group(1))
            device_info['network_os_version'] = match.group(1)

        routerboard = self.get(b'/system routerboard print')
        data_b = to_text(routerboard, errors='surrogate_or_strict').strip()
        display.vvvv("result: '%s'" % str(data_b))
        match = re.search(r'model: (.+)$', data_b, re.M)
        if match:
            device_info['network_os_model'] = match.group(1)

        identity = self.get(b'/system identity print')
        data_c = to_text(identity, errors='surrogate_or_strict').strip()
        display.vvvv("result: '%s'" % str(data_c))
        match = re.search(r'name: (.+)$', data_c, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    def get_config(self, source='running', format='text', flags=None):
        display.vvvv('get_config')
        if source not in ('running', 'startup'):
            return self.invalid_params("fetching configuration from %s is not supported" % source)
        if source == 'running':
            cmd = 'show running-config '
            if not flags:
                flags = ['all']
        else:
            cmd = 'show startup-config'

        cmd += ' '.join(to_list(flags))
        cmd = cmd.strip()

        return self.send_command(cmd)

    def edit_config(self, command):
        display.vvvv('edit_config')
        for cmd in chain(['configure terminal'], to_list(command), ['end']):
            if isinstance(cmd, dict):
                command = cmd['command']
                prompt = cmd['prompt']
                answer = cmd['answer']
                newline = cmd.get('newline', True)
            else:
                command = cmd
                prompt = None
                answer = None
                newline = True

            self.send_command(command, prompt, answer, False, newline)

    def get(self, command, prompt=None, answer=None, sendonly=False):
        display.vvvv("get: '%s'" % str(command))
        return self.send_command(command, prompt=prompt, answer=answer, sendonly=sendonly)

    def get_capabilities(self):
        display.vvvv('get_capabilities')
        result = {}
        result['rpc'] = self.get_base_rpc()
        result['network_api'] = 'cliconf'
        result['device_info'] = self.get_device_info()
        return json.dumps(result)
