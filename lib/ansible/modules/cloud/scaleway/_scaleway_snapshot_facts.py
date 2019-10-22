#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['deprecated'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: scaleway_snapshot_facts
deprecated:
  removed_in: '2.13'
  why: Deprecated in favour of C(_info) module.
  alternative: Use M(scaleway_snapshot_info) instead.
short_description: Gather facts about the Scaleway snapshots available.
description:
  - Gather facts about the Scaleway snapshot available.
version_added: "2.7"
author:
  - "Yanis Guenane (@Spredzy)"
  - "Remy Leone (@sieben)"
extends_documentation_fragment: scaleway
options:
  region:
    version_added: "2.8"
    description:
     - Scaleway region to use (for example par1).
    required: true
    choices:
      - ams1
      - EMEA-NL-EVS
      - par1
      - EMEA-FR-PAR1
'''

EXAMPLES = r'''
- name: Gather Scaleway snapshots facts
  scaleway_snapshot_facts:
    region: par1
'''

RETURN = r'''
---
scaleway_snapshot_facts:
  description: Response from Scaleway API
  returned: success
  type: complex
  sample:
    "scaleway_snapshot_facts": [
      {
          "base_volume": {
              "id": "68386fae-4f55-4fbf-aabb-953036a85872",
              "name": "snapshot-87fc282d-f252-4262-adad-86979d9074cf-2018-04-26_12:42"
          },
          "creation_date": "2018-08-14T22:34:35.299461+00:00",
          "id": "b61b4b03-a2e9-4da5-b5ea-e462ac0662d2",
          "modification_date": "2018-08-14T22:34:54.520560+00:00",
          "name": "snapshot-87fc282d-f252-4262-adad-86979d9074cf-2018-04-26_12:42 snapshot",
          "organization": "3f709602-5e6c-4619-b80c-e841c89734af",
          "size": 25000000000,
          "state": "available",
          "volume_type": "l_ssd"
      }
    ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.scaleway import (
    Scaleway,
    ScalewayException,
    scaleway_argument_spec,
    SCALEWAY_LOCATION
)


class ScalewaySnapshotFacts(Scaleway):

    def __init__(self, module):
        super(ScalewaySnapshotFacts, self).__init__(module)
        self.name = 'snapshots'

        region = module.params["region"]
        self.module.params['api_url'] = SCALEWAY_LOCATION[region]["api_endpoint"]


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        region=dict(required=True, choices=SCALEWAY_LOCATION.keys()),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        module.exit_json(
            ansible_facts={'scaleway_snapshot_facts': ScalewaySnapshotFacts(module).get_resources()}
        )
    except ScalewayException as exc:
        module.fail_json(msg=exc.message)


if __name__ == '__main__':
    main()
