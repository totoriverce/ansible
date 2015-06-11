# (c) 2012, Daniel Hokka Zakrisson <daniel@hozac.com>
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
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import codecs

from ansible.errors import *
from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        ret = []
        for term in terms:
            basedir_path  = self._loader.path_dwim(term)
            relative_path = None
            playbook_path = None

            # Special handling of the file lookup, used primarily when the
            # lookup is done from a role. If the file isn't found in the
            # basedir of the current file, use dwim_relative to look in the
            # role/files/ directory, and finally the playbook directory
            # itself (which will be relative to the current working dir)

            if 'role_path' in variables:
                relative_path = self._loader.path_dwim_relative(variables['role_path'], 'files', term)

            # FIXME: the original file stuff still needs to be worked out, but the
            #        playbook_dir stuff should be able to be removed as it should
            #        be covered by the fact that the loader contains that info
            if 'playbook_dir' in variables:
                playbook_path = self._loader.path_dwim_relative(variables['playbook_dir'],'files', term)

            for path in (basedir_path, relative_path, playbook_path):
                try:
                    contents, show_data = self._loader._get_file_contents(path)
                    ret.append(contents.rstrip())
                    break
                except AnsibleParserError:
                    continue
            else:
                raise AnsibleError("could not locate file in lookup: %s" % term)

        return ret
