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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.compat.tests.mock import patch
from ansible.modules.network.iosxr import iosxr_banner
from .iosxr_module import TestIosxrModule, load_fixture, set_module_args


class TestIosxrBannerModule(TestIosxrModule):

    module = iosxr_banner

    def setUp(self):
        self.mock_get_config = patch('ansible.modules.network.iosxr.iosxr_banner.get_config')
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch('ansible.modules.network.iosxr.iosxr_banner.load_config')
        self.load_config = self.mock_load_config.start()

    def tearDown(self):
        self.mock_get_config.stop()
        self.mock_load_config.stop()

    def load_fixtures(self, commands=None):
        self.load_config.return_value = dict(diff=None, session='session')

    def test_iosxr_banner_create(self):
        set_module_args(dict(banner='login', text='test\nbanner\nstring'))
        commands = ['banner login test\nbanner\nstring']
        self.execute_module(changed=True, commands=commands)

    def test_iosxr_banner_remove(self):
        set_module_args(dict(banner='login', state='absent'))
        commands = ['no banner login']
        self.execute_module(changed=True, commands=commands)
