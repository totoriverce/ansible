# (c) 2014, Chris Church <chris@ninemoreminutes.com>
#
# This file is part of Ansible.
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

import base64
import os
import re
import random
import shlex
import time

_common_args = ['PowerShell', '-NoProfile', '-NonInteractive']

# Primarily for testing, allow explicitly specifying PowerShell version via
# an environment variable.
_powershell_version = os.environ.get('POWERSHELL_VERSION', None)
if _powershell_version:
    _common_args = ['PowerShell', '-Version', _powershell_version] + _common_args[1:]

def _escape(value, include_vars=False):
    '''Return value escaped for use in PowerShell command.'''
    # http://www.techotopia.com/index.php/Windows_PowerShell_1.0_String_Quoting_and_Escape_Sequences
    # http://stackoverflow.com/questions/764360/a-list-of-string-replacements-in-python
    subs = [('\n', '`n'), ('\r', '`r'), ('\t', '`t'), ('\a', '`a'),
            ('\b', '`b'), ('\f', '`f'), ('\v', '`v'), ('"', '`"'),
            ('\'', '`\''), ('`', '``'), ('\x00', '`0')]
    if include_vars:
        subs.append(('$', '`$'))
    pattern = '|'.join('(%s)' % re.escape(p) for p, s in subs)
    substs = [s for p, s in subs]
    replace = lambda m: substs[m.lastindex - 1]
    return re.sub(pattern, replace, value)

def _encode_script(script, as_list=False):
    '''Convert a PowerShell script to a single base64-encoded command.'''
    script = '\n'.join([x.strip() for x in script.splitlines() if x.strip()])
    encoded_script = base64.b64encode(script.encode('utf-16-le'))
    cmd_parts = _common_args + ['-EncodedCommand', encoded_script]
    if as_list:
        return cmd_parts
    return ' '.join(cmd_parts)

def _build_file_cmd(cmd_parts):
    '''Build command line to run a file, given list of file name plus args.'''
    return ' '.join(_common_args + ['-ExecutionPolicy', 'Unrestricted', '-File'] + ['"%s"' % x for x in cmd_parts])

class ShellModule(object):

    def env_prefix(self, **kwargs):
        return ''

    def join_path(self, *args):
        return os.path.join(*args).replace('/', '\\')

    def path_has_trailing_slash(self, path):
        # Allow Windows paths to be specified using either slash.
        return path.endswith('/') or path.endswith('\\')

    def chmod(self, mode, path):
        return ''

    def remove(self, path, recurse=False):
        path = _escape(path)
        if recurse:
            return _encode_script('''Remove-Item "%s" -Force -Recurse;''' % path)
        else:
            return _encode_script('''Remove-Item "%s" -Force;''' % path)

    def mkdtemp(self, basefile, system=False, mode=None):
        basefile = _escape(basefile)
        # FIXME: Support system temp path!
        return _encode_script('''(New-Item -Type Directory -Path $env:temp -Name "%s").FullName | Write-Host -Separator '';''' % basefile)

    def md5(self, path):
        path = _escape(path)
        script = '''
            If (Test-Path -PathType Leaf "%(path)s")
            {
                (Get-FileHash -Path "%(path)s" -Algorithm MD5).Hash.ToLower();
            }
            ElseIf (Test-Path -PathType Container "%(path)s")
            {
                Write-Host "3";
            }
            Else
            {
                Write-Host "1";
            }
        ''' % dict(path=path)
        return _encode_script(script)

    def build_module_command(self, env_string, shebang, cmd, rm_tmp=None):
        cmd_parts = shlex.split(cmd, posix=False)
        if not cmd_parts[0].lower().endswith('.ps1'):
            cmd_parts[0] = '%s.ps1' % cmd_parts[0]
        script = _build_file_cmd(cmd_parts)
        if rm_tmp:
            rm_tmp = _escape(rm_tmp)
            script = '%s; Remove-Item "%s" -Force -Recurse;' % (script, rm_tmp)
        return _encode_script(script)
