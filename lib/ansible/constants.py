# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
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

import os


# control side (aka 'overlord')
DEFAULT_HOST_LIST      = os.environ.get('ANSIBLE_HOSTS',
                                        '/etc/ansible/hosts')
DEFAULT_MODULE_PATH    = os.environ.get('ANSIBLE_LIBRARY',
                                        '/usr/share/ansible')
DEFAULT_MODULE_NAME    = 'command'
DEFAULT_PATTERN        = '*'
DEFAULT_FORKS          = 5
DEFAULT_MODULE_ARGS    = ''
DEFAULT_TIMEOUT        = 10
DEFAULT_POLL_INTERVAL  = 15
DEFAULT_REMOTE_USER    = 'root'
DEFAULT_REMOTE_PASS    = None
DEFAULT_REMOTE_PORT    = 22
