# coding: utf-8
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

import io

from units.compat import unittest
from ansible.parsing import vault
from ansible.parsing.yaml import dumper, objects
from ansible.parsing.yaml.loader import AnsibleLoader
from ansible.utils.unsafe_proxy import AnsibleUnsafeText, AnsibleUnsafeBytes

from units.mock.yaml_helper import YamlTestUtils
from units.mock.vault_helper import TextVaultSecret


class TestAnsibleDumper(unittest.TestCase, YamlTestUtils):
    def setUp(self):
        self.vault_password = "hunter42"
        vault_secret = TextVaultSecret(self.vault_password)
        self.vault_secrets = [('vault_secret', vault_secret)]
        self.good_vault = vault.VaultLib(self.vault_secrets)
        self.vault = self.good_vault
        self.stream = self._build_stream()
        self.dumper = dumper.AnsibleDumper

    def _build_stream(self, yaml_text=None):
        text = yaml_text or u''
        stream = io.StringIO(text)
        return stream

    def _loader(self, stream):
        return AnsibleLoader(stream, vault_secrets=self.vault.secrets)

    def test_ansible_vault_encrypted_unicode(self):
        plaintext = 'This is a string we are going to encrypt.'
        avu = objects.AnsibleVaultEncryptedUnicode.from_plaintext(plaintext, vault=self.vault,
                                                                  secret=vault.match_secrets(self.vault_secrets, ['vault_secret'])[0][1])

        yaml_out = self._dump_string(avu, dumper=self.dumper)
        stream = self._build_stream(yaml_out)
        loader = self._loader(stream)

        data_from_yaml = loader.get_single_data()

        self.assertEqual(plaintext, data_from_yaml.data)

    def test_bytes(self):
        b_text = b'some bytes'
        f = AnsibleUnsafeBytes(b_text)
        yaml_out = self._dump_string(f, dumper=self.dumper)

        stream = self._build_stream(yaml_out)
        loader = self._loader(stream)

        data_from_yaml = loader.get_single_data()

        self.assertEqual(b_text, data_from_yaml)


    def test_unicode(self):
        u_text = u'some unicode'
        f = AnsibleUnsafeText(u_text)
        yaml_out = self._dump_string(f, dumper=self.dumper)

        stream = self._build_stream(yaml_out)
        loader = self._loader(stream)

        data_from_yaml = loader.get_single_data()

        self.assertEqual(u_text, data_from_yaml)

    def test_native_text(self):
        n_text = 'some native text'
        f = AnsibleUnsafeText(n_text)
        yaml_out = self._dump_string(f, dumper=self.dumper)

        stream = self._build_stream(yaml_out)
        loader = self._loader(stream)

        data_from_yaml = loader.get_single_data()

        self.assertEqual(n_text, data_from_yaml)
