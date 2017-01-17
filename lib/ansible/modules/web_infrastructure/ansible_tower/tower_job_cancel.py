#!/usr/bin/env python
#coding: utf-8 -*-

# (c) 2016, Wayne Witzel III <wayne@riotousliving.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: tower_job_cancel
version_added: "2.3"
short_description: Cancel an Ansible Tower Job.
description:
    - Cancel Ansible Tower jobs. See
      U(https://www.ansible.com/tower) for an overview.
options:
    job_id:
      description:
        - ID of the job to cancel
      required: True
      default: null
    fail_if_not_running:
      description:
        - Fail loudly if the job_id does not reference a running job.
      required: False
      default: False
    config_file:
      description:
        - Path to the Tower config file. See notes.
      required: False
      default: null


requirements:
  - "python >= 2.6"
  - "ansible-tower-cli >= 3.0.3"

notes:
  - If no I(config_file) is provided we will attempt to use the tower-cli library
    defaults to find your Tower host information.
  - I(config_file) should contain Tower configuration in the following format:
      host=hostname
      username=username
      password=password
'''


EXAMPLES = '''
    tower_job_cancel:
        job_id: 5
        config_file: "~/tower_cli.cfg"
'''

import os

try:
    import tower_cli
    import tower_cli.utils.exceptions as exc
    from tower_cli.utils import parser
    from tower_cli.conf import settings

    HAS_TOWER_CLI = True
except ImportError:
    HAS_TOWER_CLI = False


def tower_auth_config(module):
    config_file = module.params.get('config_file')
    if not config_file:
        return {}

    config_file = os.path.expanduser(config_file)
    if not os.path.exists(config_file):
        module.fail_json(msg='file not found: %s' % config_file)
    if os.path.isdir(config_file):
        module.fail_json(msg='directory can not be used as config file: %s' % config_file)

    with open(config_file, 'rb') as f:
        return parser.string_to_dict(f.read())


def main():
    module = AnsibleModule(
        argument_spec = dict(
            job_id = dict(type='int', required=True),
            fail_if_not_running = dict(type='bool', default=False),
            config_file = dict(),
        ),
        supports_check_mode=False
    )

    if not HAS_TOWER_CLI:
        module.fail_json(msg='ansible-tower-cli required for this module')

    job_id = module.params.get('job_id')
    json_output = {}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        job = tower_cli.get_resource('job')
        params = module.params.copy()

        try:
            result = job.cancel(job_id, **params)
        except exc.TowerCLIError as excinfo:
            module.fail_json(msg='job_id: {}. {}'.format(job_id, excinfo), changed=False)
        except (exc.ConnectionError, exc.BadRequest) as excinfo:
            module.fail_json(msg='{}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)


from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
