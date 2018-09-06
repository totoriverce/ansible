# -*- coding: utf-8 -*-
# (c) 2018, Scott Buchanan <sbuchanan@ri.pn>
# (c) 2016, Andrew Zenk <azenk@umn.edu> (lastpass.py used as starting point)
# (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
    lookup: onepassword_raw
    author:
      - Scott Buchanan <sbuchanan@ri.pn>
      - Andrew Zenk <azenk@umn.edu>
      - Sam Doran <sdoran@redhat.com>
    version_added: "2.6"
    requirements:
      - C(op) 1Password command line utility. See U(https://support.1password.com/command-line/)
    short_description: fetch an entire item from 1Password
    description:
      - C(onepassword_raw) wraps C(op) command line utility to fetch an entire item from 1Password
    options:
      _terms:
        description: identifier(s) (UUID, name, or domain; case-insensitive) of item(s) to retrieve
        required: True
      master_password:
        description: The password used to unlock the specified vault.
        default: None
        version_added: '2.7'
        aliases: ['vault_password']
      section:
        description: Item section containing the field to retrieve (case-insensitive). If absent will return first match from any section.
        default: None
      subdomain:
        description: The 1Password subdomain to authenticate against.
        default: None
        version_added: '2.7'
      username:
        description: The username used to sign in.
        version_added: '2.7'
      secret_key:
        description: The secret key used when performing an initial sign in.
        version_added: '2.7'
      vault:
        description: Vault containing the item to retrieve (case-insensitive). If absent will search all vaults
        default: None
"""

EXAMPLES = """
- name: Retrieve all data about Wintermute
  debug:
    var: lookup('onepassword_raw', 'Wintermute')

- name: Retrieve all data about Wintermute when not signed in to 1Password
  debug:
    var: lookup('onepassword_raw', 'Wintermute', subdomain='Turing', vault_password='DmbslfLvasjdl')
"""

RETURN = """
  _raw:
    description: field data requested
"""

import json

from ansible.plugins.lookup.onepassword import OnePass
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        op = OnePass()

        vault = kwargs.get('vault')
        op.subdomain = kwargs.get('subdomain')
        op.username = kwargs.get('username')
        op.secret_key = kwargs.get('secret_key')
        op.master_password = kwargs.get('master_password', kwargs.get('vault_password'))

        op.assert_logged_in()

        values = []
        for term in terms:
            data = json.loads(op.get_raw(term, vault))
            values.append(data)
        return values
