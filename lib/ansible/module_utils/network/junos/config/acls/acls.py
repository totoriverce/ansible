#
# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The junos_acls class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.network.common.cfg.base import ConfigBase
from ansible.module_utils.network.common.utils import to_list
from ansible.module_utils.network.junos.facts.facts import Facts
from ansible.module_utils.network.junos.junos import (locked_config,
                                                      load_config,
                                                      commit_configuration,
                                                      discard_changes,
                                                      tostring)
from ansible.module_utils.network.common.netconf import (build_root_xml_node,
                                                         build_child_xml_node)


class Acls(ConfigBase):
    """
    The junos_acls class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'acls',
    ]

    def __init__(self, module):
        super(Acls, self).__init__(module)

    def get_acls_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        acls_facts = facts['ansible_network_resources'].get('junos_acls')
        if not acls_facts:
            return []
        return acls_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()

        existing_acls_facts = self.get_acls_facts()
        config_xmls = self.set_config(existing_acls_facts)

        with locked_config(self._module):
            for config_xml in to_list(config_xmls):
                diff = load_config(self._module, config_xml, [])

            commit = not self._module.check_mode
            if diff:
                if commit:
                    commit_configuration(self._module)
                else:
                    discard_changes(self._module)
                result['changed'] = True

                if self._module._diff:
                    result['diff'] = {'prepared': diff}

        result['xml'] = config_xmls
        changed_acls_facts = self.get_acls_facts()

        result['before'] = existing_acls_facts
        if result['changed']:
            result['after'] = changed_acls_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_acls_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_acls_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        root = build_root_xml_node('firewall')
        state = self._module.params['state']
        if state == 'overridden':
            config_xmls = self._state_overridden(want, have)
        elif state == 'deleted':
            config_xmls = self._state_deleted(want, have)
        elif state == 'merged':
            config_xmls = self._state_merged(want, have)
        elif state == 'replaced':
            config_xmls = self._state_replaced(want, have)

        for xml in config_xmls:
            root.append(xml)

        return tostring(root)

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the xml necessary to migrate the current configuration
                  to the desired configuration
        """
        acls_xml = []
        return acls_xml

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the xml necessary to migrate the current configuration
                  to the desired configuration
        """
        acls_xml = []
        return acls_xml

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the xml necessary to migrate the current configuration
                  to the desired configuration
        """
        acls_xml = []
        return acls_xml

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the xml necessary to migrate the current configuration
                  to the desired configuration
        """
        acls_xml = []
        family_node = build_root_xml_node('family')
        inet_node = build_child_xml_node(family_node, 'inet')
        for config in want:
            for acl in config['acls']:
                filter_node = build_child_xml_node(inet_node, 'filter')
                build_child_xml_node(filter_node, 'name', acl['name'])
                if acl.get('aces'):
                    for ace in acl['aces']:
                        term_node = build_child_xml_node(filter_node, 'term')
                        build_child_xml_node(term_node, 'name', ace['name'])
                        if ace.get('protocol') or ace.get('port'):
                            from_node = build_child_xml_node(term_node, 'from')
                            if ace['protocol']:
                                if 'range' not in ace['protocol'].keys():
                                    protocol = list(ace['protocol'].keys())[0]
                                    build_child_xml_node(from_node, 'protocol', protocol)
                            if ace['port']:
                                build_child_xml_node(from_node, 'port', ace['port']['range'])
        acls_xml.append(family_node)
        return acls_xml
