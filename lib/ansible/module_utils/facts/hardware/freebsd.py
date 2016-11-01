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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import re

from ansible.module_utils.facts.hardware.base import Hardware, HardwareCollector
from ansible.module_utils.facts.timeout import TimeoutError, timeout

from ansible.module_utils.facts.utils import get_file_content, get_mount_size


class FreeBSDHardware(Hardware):
    """
    FreeBSD-specific subclass of Hardware.  Defines memory and CPU facts:
    - memfree_mb
    - memtotal_mb
    - swapfree_mb
    - swaptotal_mb
    - processor (a list)
    - processor_cores
    - processor_count
    - devices
    """
    platform = 'FreeBSD'
    DMESG_BOOT = '/var/run/dmesg.boot'

    def populate(self, collected_facts=None):
        hardware_facts = {}

        cpu_facts = self.get_cpu_facts()
        memory_facts = self.get_memory_facts()
        dmi_facts = self.get_dmi_facts()
        device_facts = self.get_device_facts()

        mount_facts = {}
        try:
            mount_facts = self.get_mount_facts()
        except TimeoutError:
            pass

        hardware_facts.update(cpu_facts)
        hardware_facts.update(memory_facts)
        hardware_facts.update(dmi_facts)
        hardware_facts.update(device_facts)
        hardware_facts.update(mount_facts)

        return hardware_facts

    def get_cpu_facts(self):
        cpu_facts = {}
        cpu_facts['processor'] = []
        rc, out, err = self.module.run_command("/sbin/sysctl -n hw.ncpu")
        cpu_facts['processor_count'] = out.strip()

        dmesg_boot = get_file_content(FreeBSDHardware.DMESG_BOOT)
        if not dmesg_boot:
            rc, dmesg_boot, err = self.module.run_command("/sbin/dmesg")
        for line in dmesg_boot.splitlines():
            if 'CPU:' in line:
                cpu = re.sub(r'CPU:\s+', r"", line)
                cpu_facts['processor'].append(cpu.strip())
            if 'Logical CPUs per core' in line:
                cpu_facts['processor_cores'] = line.split()[4]

        return cpu_facts

    def get_memory_facts(self):
        memory_facts = {}

        rc, out, err = self.module.run_command("/sbin/sysctl vm.stats")
        for line in out.splitlines():
            data = line.split()
            if 'vm.stats.vm.v_page_size' in line:
                pagesize = int(data[1])
            if 'vm.stats.vm.v_page_count' in line:
                pagecount = int(data[1])
            if 'vm.stats.vm.v_free_count' in line:
                freecount = int(data[1])
        memory_facts['memtotal_mb'] = pagesize * pagecount // 1024 // 1024
        memory_facts['memfree_mb'] = pagesize * freecount // 1024 // 1024
        # Get swapinfo.  swapinfo output looks like:
        # Device          1M-blocks     Used    Avail Capacity
        # /dev/ada0p3        314368        0   314368     0%
        #
        rc, out, err = self.module.run_command("/usr/sbin/swapinfo -k")
        lines = out.splitlines()
        if len(lines[-1]) == 0:
            lines.pop()
        data = lines[-1].split()
        if data[0] != 'Device':
            memory_facts['swaptotal_mb'] = int(data[1]) // 1024
            memory_facts['swapfree_mb'] = int(data[3]) // 1024

        return memory_facts

    @timeout()
    def get_mount_facts(self):
        mount_facts = {}

        mount_facts['mounts'] = []
        fstab = get_file_content('/etc/fstab')
        if fstab:
            for line in fstab.splitlines():
                if line.startswith('#') or line.strip() == '':
                    continue
                fields = re.sub(r'\s+', ' ', line).split()
                size_total, size_available = get_mount_size(fields[1])
                mount_facts['mounts'].append({
                    'mount': fields[1],
                    'device': fields[0],
                    'fstype': fields[2],
                    'options': fields[3],
                    'size_total': size_total,
                    'size_available': size_available
                })

        return mount_facts

    def get_device_facts(self):
        device_facts = {}

        sysdir = '/dev'
        device_facts['devices'] = {}
        drives = re.compile('(ada?\d+|da\d+|a?cd\d+)')  # TODO: rc, disks, err = self.module.run_command("/sbin/sysctl kern.disks")
        slices = re.compile('(ada?\d+s\d+\w*|da\d+s\d+\w*)')
        if os.path.isdir(sysdir):
            dirlist = sorted(os.listdir(sysdir))
            for device in dirlist:
                d = drives.match(device)
                if d:
                    device_facts['devices'][d.group(1)] = []
                s = slices.match(device)
                if s:
                    device_facts['devices'][d.group(1)].append(s.group(1))

        return device_facts

    def get_dmi_facts(self):
        ''' learn dmi facts from system

        Use dmidecode executable if available'''

        dmi_facts = {}

        # Fall back to using dmidecode, if available
        dmi_bin = self.module.get_bin_path('dmidecode')
        DMI_DICT = dict(
            bios_date='bios-release-date',
            bios_version='bios-version',
            form_factor='chassis-type',
            product_name='system-product-name',
            product_serial='system-serial-number',
            product_uuid='system-uuid',
            product_version='system-version',
            system_vendor='system-manufacturer'
        )
        for (k, v) in DMI_DICT.items():
            if dmi_bin is not None:
                (rc, out, err) = self.module.run_command('%s -s %s' % (dmi_bin, v))
                if rc == 0:
                    # Strip out commented lines (specific dmidecode output)
                    # FIXME: why add the fact and then test if it is json?
                    dmi_facts[k] = ''.join([line for line in out.splitlines() if not line.startswith('#')])
                    try:
                        json.dumps(dmi_facts[k])
                    except UnicodeDecodeError:
                        dmi_facts[k] = 'NA'
                else:
                    dmi_facts[k] = 'NA'
            else:
                dmi_facts[k] = 'NA'

        return dmi_facts


class FreeBSDHardwareCollector(HardwareCollector):
    _fact_class = FreeBSDHardware
    _platform = 'FreeBSD'
