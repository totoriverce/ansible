#!/usr/bin/python

# In cisco IOS, seems that the only way to find out the max number of vty
# is via the command "show line vty ?". This generate an stderr tahta can be registered
# on a variable and with this filter we can extrac the max number of vty configurable

# - name: EXTRACT VTY LINE RANGE
#   ios_command:
#     commands:
#       - show line vty ?
#   ignore_errors: True
#   register: vty_line_range
#   notify: save config
# - debug: var=vty_line_range
#
# - name: CREATE DYNAMIC VARIABLE FOR VALID SNMP SERVER SYNTAX
#   set_fact:
#     syntax_t2c_vty: "{{ vty_line_range.module_stderr }}"
# - debug: var=syntax_t2c_vty
#
# - name: REMOVE UNWANTED SNMP SERVER FROM T2C ROUTER
#   ios_config:
#     lines:
#       - line vty 0 {{ syntax_t2c_vty }}
#   with_items: "{{ syntax_t2c_vty | vty_filter }}"

import re

class FilterModule(object):
    def filters(self):
        return { 'vty_filter': self.vty_filter }


    def vty_filter(self, stderr_var):
        match = re.search(r'<\d-(\d+)>', stderr_var, re.M)
        vty_max = match.group(1)
        return vty_max
