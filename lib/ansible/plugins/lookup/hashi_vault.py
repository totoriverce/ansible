# (c) 2015, Jonathan Davila <jdavila(at)ansible.com>
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
# USAGE: {{ lookup('hashi_vault', 'secret=secret/hello:value token=c975b780-d1be-8016-866b-01d0f9b688a5 url=http://myvault:8200')}}
#
# You can skip setting the url if you set the VAULT_ADDR environment variable
# or if you want it to default to localhost:8200
#
# The `key` argument allows a key of any depth to be specified in `dot.separated.format`
#
# Multiple authentication backends are supported. It is advised against specified
# more than one authentication method, nevertheless they will take the following
# order of preference:
#
# + *TLS* kwargs: `tls-cert` and `tls-key`
# + *TOKEN* kwargs: `token`
# + *USERNAME AND PASSWORD* kwargs: `username` and `password`
# + *LDAP* kwargs: `ldap-user` and `ldap-pass`
# + *GITHUB TOKEN* kwargs: `github`
# + *APP-ID* kwargs: `app-id` and `user-id`
#
# Multi-Factor authentication is not yet supported.
#
# NOTE: Due to a current limitation in the HVAC library there won't
# necessarily be an error if a bad endpoint is specified.
#
# Requires hvac library. Install with pip.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


ANSIBLE_HASHI_VAULT_ADDR = 'http://127.0.0.1:8200'

if os.getenv('VAULT_ADDR') is not None:
    ANSIBLE_HASHI_VAULT_ADDR = os.environ['VAULT_ADDR']

class HashiVault:
    def __init__(self, **kwargs):
        try:
            import hvac
        except ImportError:
            AnsibleError("Please pip install hvac to use this module")

        self.url = kwargs.get('url', ANSIBLE_HASHI_VAULT_ADDR)

        # split secret arg, which has format 'secret/hello:value' into secret='secret/hello' and secret_field='value'
        s = kwargs.get('secret')
        if s==None:
            raise AnsibleError("No secret specified")

        s_f = s.split(':')
        self.secret = s_f[0]
        if len(s_f)>=2:
            self.secret_field = s_f[1]
        else:
            self.secret_field = 'value'

        self.token = kwargs.get('token', None)
        self.appid = kwargs.get('app-id', None)
        self.usrid = kwargs.get('user-id', None)
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        self.github = kwargs.get('github', None)
        self.ldapusr = kwargs.get('ldap-user', None)
        self.ldappwd = kwargs.get('ldap-pass', None)
        self.tlscert = kwargs.get('tls-cert', None)
        self.tlskey = kwargs.get('tls-key', None)

        if not any((self.token, self.github,
                    self.appid and self.usrid,
                    self.username and self.password,
                    self.ldapusr and self.ldappwd,
                    self.tlscert and self.tlskey)):
            raise AnsibleError("No valid authentication method found")

        if self.tlscert:
            self.client = hvac.Client(url=self.url,
                                      cert=(self.tlscert, self.tlskey))
            if self.client.is_authenticated():
                pass
            else:
                raise AnsibleError("Invalid TLS certificate specified")
        else:
            self.client = hvac.Client(url=self.url)

        if self.token:
            self.client.token = self.token
        elif self.username:
            self.client.auth_userpass(self.username, self.password)
        elif self.ldapusr:
            self.client.auth_ldap(self.ldapusr, self.ldappwd)
        elif self.github:
            self.client.auth_github(self.github)
        elif self.appid:
            self.client.auth_app_id(self.appid, self.usrid)

        if self.client.is_authenticated():
            pass
        else:
            raise AnsibleError("Invalid Hashicorp Vault Credentials Specified")

    def get(self):
        data = self.client.read(self.secret)
        if data is None:
            raise AnsibleError("The secret %s doesn't seem to exist" % self.secret)

        if self.secret_field=='': # secret was specified with trailing ':'
            return data['data']
        else:
            try:
                for key in ['data'] + self.secret_field.split('.'):
                    data = data[key]
                return data
            except KeyError:
                AnsibleError("The secret %s doesn't seem to have the requested key %s" % (self.secret, self.secret_field))


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        vault_args = terms[0].split(' ')
        vault_dict = {}
        ret = []

        for param in vault_args:
            try:
                key, value = param.split('=')
            except ValueError as e:
                raise AnsibleError("hashi_vault plugin needs key=value pairs, but received %s" % terms)
            vault_dict[key] = value

        vault_conn = HashiVault(**vault_dict)

        for term in terms:
           key = term.split()[0]
           value = vault_conn.get()
           ret.append(value)

        return ret
