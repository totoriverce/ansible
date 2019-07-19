#
# Copyright (c) 2019 Ericsson AB.
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = """
options:
   provider:
    description:
      - B(Deprecated)
      - "Starting with Ansible 2.5 we recommend using C(connection: network_cli)."
      - HORIZONTALLINE
      - A dict object containing connection details.
    type: dict
    suboptions:
      host:
	description:
	  - Specifies the DNS host name or address for connecting to the remote
	    device over the specified transport.  The value of host is used as
	    the destination address for the transport.
	required: true
      port:
	description:
	  - Specifies the port to use when building the connection to the remote device.
	default: 22
      username:
	description:
	  - Configures the username to use to authenticate the connection to
	    the remote device.  This value is used to authenticate
	    the SSH session. If the value is not specified in the task, the
	    value of environment variable C(ANSIBLE_NET_USERNAME) will be used instead.
      password:
	description:
	  - Specifies the password to use to authenticate the connection to
	    the remote device.   This value is used to authenticate
	    the SSH session. If the value is not specified in the task, the
	    value of environment variable C(ANSIBLE_NET_PASSWORD) will be used instead.
      timeout:
	description:
	  - Specifies the timeout in seconds for communicating with the network device
	    for either connecting or sending commands.  If the timeout is
	    exceeded before the operation is completed, the module will error.
	default: 10
      ssh_keyfile:
	description:
	  - Specifies the SSH key to use to authenticate the connection to
	    the remote device.   This value is the path to the
	    key used to authenticate the SSH session. If the value is not specified
	    in the task, the value of environment variable C(ANSIBLE_NET_SSH_KEYFILE)
	    will be used instead.
      authorize:
	description:
	  - Instructs the module to enter privileged mode on the remote device
	    before sending any commands.  If not specified, the device will
	    attempt to execute all commands in non-privileged mode. If the value
	    is not specified in the task, the value of environment variable
	    C(ANSIBLE_NET_AUTHORIZE) will be used instead.
	type: bool
	default: 'no'
      auth_pass:
	description:
	  - Specifies the password to use if required to enter privileged mode
	    on the remote device.  If I(authorize) is false, then this argument
	    does nothing. If the value is not specified in the task, the value of
	    environment variable C(ANSIBLE_NET_AUTH_PASS) will be used instead.
notes:
  - For more information on using Ansible to manage network devices see the :ref:`Ansible Network Guide <network_guide>`
  - For more information on using Ansible to manage Ericsson devices see the Ericsson documents.
"""
