# (c) 2015, Brian Coca  <briancoca+dev@gmail.com>
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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible.plugins.action import ActionBase
from ansible.utils.boolean import boolean


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        src        = self._task.args.get('src', None)
        remote_src = boolean(self._task.args.get('remote_src', 'no'))
        remote_user = task_vars.get('ansible_ssh_user') or self._play_context.remote_user

        if src is None:
            result['failed'] = True
            result['msg'] = "src is required"
            return result
        elif remote_src:
            # everything is remote, so we just execute the module
            # without changing any of the module arguments
            result.update(self._execute_module(task_vars=task_vars))
            return result

        if self._task._role is not None:
            src = self._loader.path_dwim_relative(self._task._role._role_path, 'files', src)
        else:
            src = self._loader.path_dwim_relative(self._loader.get_basedir(), 'files', src)

        # create the remote tmp dir if needed, and put the source file there
        if tmp is None or "-tmp-" not in tmp:
            tmp = self._make_tmp_path(remote_user)
            self._cleanup_remote_tmp = True

        tmp_src = self._connection._shell.join_path(tmp, os.path.basename(src))
        self._transfer_file(src, tmp_src)

        self._fixup_perms(tmp, remote_user, recursive=True)

        new_module_args = self._task.args.copy()
        new_module_args.update(
            dict(
                src=tmp_src,
            )
        )

        result.update(self._execute_module('patch', module_args=new_module_args, task_vars=task_vars))
        self._remove_tmp_path(tmp)
        return result
