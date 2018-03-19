# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import MagicMock
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook import Playbook
from ansible.template import Templar

from units.mock.loader import DictDataLoader


class TestPlaybookExecutor(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_serialized_batches(self):
        fake_loader = DictDataLoader({
            'no_serial.yml': '''
            - hosts: all
              gather_facts: no
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_int.yml': '''
            - hosts: all
              gather_facts: no
              serial: 2
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_pct.yml': '''
            - hosts: all
              gather_facts: no
              serial: 20%
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_list.yml': '''
            - hosts: all
              gather_facts: no
              serial: [1, 2, 3]
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_list_mixed.yml': '''
            - hosts: all
              gather_facts: no
              serial: [1, "20%", -1]
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_no_unreachable.yml': '''
            - hosts: all
              gather_facts: no
              serial: [[2, 1]]
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_pct_no_unreachable.yml': '''
            - hosts: all
              gather_facts: no
              serial: [[20%, 1]]
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_list_no_unreachable.yml': '''
            - hosts: all
              gather_facts: no
              serial: [[1, 1], 2, [3, 0]]
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_list_no_unreachable_mixed.yml': '''
            - hosts: all
              gather_facts: no
              serial: [1, ["20%", 1], [-1, 1]]
              tasks:
              - debug: var=inventory_hostname
            ''',
            'serial_list_no_unreachable_inv.yml': '''
            - hosts: all
              gather_facts: no
              serial: [[1, 1], [2, "not_valid"], [2, 1], [2, 10], [2, 0], 1]
              tasks:
              - debug: var=inventory_hostname
            ''',
        })

        mock_inventory = MagicMock()
        mock_var_manager = MagicMock()

        # fake out options to use the syntax CLI switch, which will ensure
        # the PlaybookExecutor doesn't create a TaskQueueManager
        mock_options = MagicMock()
        mock_options.syntax.value = True

        templar = Templar(loader=fake_loader)

        pbe = PlaybookExecutor(
            playbooks=['no_serial.yml', 'serial_int.yml', 'serial_pct.yml', 'serial_list.yml', 'serial_list_mixed.yml',
                       'serial_no_unreachable.yml', 'serial_pct_no_unreachable.yml', 'serial_list_no_unreachable.yml',
                       'serial_list_no_unreachable_mixed.yml', 'serial_list_no_unreachable_inv.yml'],
            inventory=mock_inventory,
            variable_manager=mock_var_manager,
            loader=fake_loader,
            options=mock_options,
            passwords=[],
        )

        playbook = Playbook.load(pbe._playbooks[0], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), ([['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']], [0]))

        playbook = Playbook.load(pbe._playbooks[1], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(
            pbe._get_serialized_batches(play),
            ([['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9']], [0, 0, 0, 0, 0])
        )

        playbook = Playbook.load(pbe._playbooks[2], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(
            pbe._get_serialized_batches(play),
            ([['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9']], [0, 0, 0, 0, 0])
        )

        playbook = Playbook.load(pbe._playbooks[3], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(
            pbe._get_serialized_batches(play),
            ([['host0'], ['host1', 'host2'], ['host3', 'host4', 'host5'], ['host6', 'host7', 'host8'], ['host9']], [0, 0, 0, 0, 0])
        )

        playbook = Playbook.load(pbe._playbooks[4], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), ([['host0'], ['host1', 'host2'], ['host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']], [0, 0, 0]))

        # Test when serial percent is under 1.0
        playbook = Playbook.load(pbe._playbooks[2], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2']
        self.assertEqual(pbe._get_serialized_batches(play), ([['host0'], ['host1'], ['host2']], [0, 0, 0]))

        # Test when there is a remainder for serial as a percent
        playbook = Playbook.load(pbe._playbooks[2], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9', 'host10']
        self.assertEqual(
            pbe._get_serialized_batches(play),
            ([['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9'], ['host10']], [0, 0, 0, 0, 0, 0])
        )
        playbook = Playbook.load(pbe._playbooks[5], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(
            pbe._get_serialized_batches(play), ([['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9']], [1,1,1,1,1])
        )

        playbook = Playbook.load(pbe._playbooks[6], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(
            pbe._get_serialized_batches(play), ([['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9']], [1, 1, 1, 1, 1])
        )

        playbook = Playbook.load(pbe._playbooks[7], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(
            pbe._get_serialized_batches(play), ([['host0'], ['host1', 'host2'], ['host3', 'host4', 'host5'], ['host6', 'host7', 'host8'], ['host9']], [1, 0, 0, 0, 0])
        )

        playbook = Playbook.load(pbe._playbooks[8], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), ([['host0'], ['host1', 'host2'],['host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']], [0, 1, 0])
        )
        playbook = Playbook.load(pbe._playbooks[9], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), ([['host0'], ['host1', 'host2'], ['host3', 'host4'], ['host5', 'host6'], ['host7', 'host8'], ['host9']], [1, 0, 1, 0, 0, 0])
        )
