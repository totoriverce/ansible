# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2016 Red Hat Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import re

from ansible.module_utils.six.moves import zip

DEFAULT_COMMENT_TOKENS = ['#', '!', '/*', '*/']


class ConfigLine(object):

    def __init__(self, raw):
        self.text = str(raw).strip()
        self.raw = raw
        self._children = list()
        self._parents = list()

    def __str__(self):
        return self.raw

    def __eq__(self, other):
        return self.line == other.line

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        for item in self._children:
            if item.text == key:
                return item
        raise KeyError(key)

    @property
    def line(self):
        line = self.parents
        line.append(self.text)
        return ' '.join(line)

    @property
    def children(self):
        return _obj_to_text(self._children)

    @property
    def parents(self):
        return _obj_to_text(self._parents)

    @property
    def path(self):
        config = _obj_to_raw(self._parents)
        config.append(self.raw)
        return '\n'.join(config)

    @property
    def has_chilren(self):
        return len(self._children) > 0

    @property
    def has_parents(self):
        return len(self._parents) > 0

    def add_child(self, obj):
        assert isinstance(obj, ConfigLine), 'child must be of type `ConfigLine`'
        self._children.append(obj)

def ignore_line(text, tokens=None):
    for item in (tokens or DEFAULT_COMMENT_TOKENS):
        if text.startswith(item):
            return True

_obj_to_text = lambda x: [o.text for o in x]
_obj_to_raw = lambda x: [o.raw for o in x]

def _obj_to_block(objects, visited=None):
    items = list()
    for o in objects:
        if o not in items:
            items.append(o)
            for child in o._children:
                if child not in items:
                    items.append(child)
    return _obj_to_raw(items)

def dumps(objects, output='block', comments=False):
    if output == 'block':
        items = _obj_to_block(objects)
    elif output == 'commands':
        items = _obj_to_text(objects)
    else:
        raise TypeError('unknown value supplied for keyword output')

    if output != 'commands':
        if comments:
            for index, item in enumerate(items):
                nextitem = index + 1
                if nextitem < len(items) and not item.startswith(' ') and items[nextitem].startswith(' '):
                    item = '!\n%s' % item
                items[index] = item
            items.append('!')
        items.append('end')

    return '\n'.join(items)

class NetworkConfig(object):

    def __init__(self, indent=1, contents=None):
        self._indent = indent
        self._items = list()

        if contents:
            self.load(contents)

    @property
    def items(self):
        return self._items

    def __getitem__(self, key):
        for line in self:
            if line.text == key:
                return line
        raise KeyError(key)

    def __iter__(self):
        return iter(self._items)

    def __str__(self):
        return '\n'.join([c.raw for c in self.items])

    def load(self, s):
        self._items = self.parse(s)

    def loadfp(self, fp):
        return self.load(open(fp).read())

    def parse(self, lines, comment_tokens=None):
        toplevel = re.compile(r'\S')
        childline = re.compile(r'^\s*(.+)$')

        ancestors = list()
        config = list()

        curlevel = 0
        prevlevel = 0

        for linenum, line in enumerate(str(lines).split('\n')):
            text = str(re.sub(r'([{};])', '', line)).strip()

            cfg = ConfigLine(line)

            if not text or ignore_line(text, comment_tokens):
                continue

            # handle top level commands
            if toplevel.match(line):
                ancestors = [cfg]
                prevlevel = curlevel
                curlevel = 0

            # handle sub level commands
            else:
                match = childline.match(line)
                line_indent = match.start(1)

                prevlevel = curlevel
                curlevel = int(line_indent / self._indent)

                if (curlevel - 1) > prevlevel:
                    curlevel = prevlevel + 1

                parent_level = curlevel - 1

                cfg._parents = ancestors[:curlevel]

                if curlevel > len(ancestors):
                    config.append(cfg)
                    continue

                for i in range(curlevel, len(ancestors)):
                    ancestors.pop()

                ancestors.append(cfg)
                ancestors[parent_level].add_child(cfg)

            config.append(cfg)

        return config

    def get_object(self, path):
        for item in self.items:
            if item.text == path[-1]:
                if item.parents == path[:-1]:
                    return item

    def get_block(self, path):
        assert isinstance(path, list), 'path argument must be a list object'
        obj = self.get_object(path)
        if not obj:
            raise ValueError('path does not exist in config')
        return self._expand_block(obj)

    def get_block_config(self, path):
        block = self.get_block(path)
        return dumps(block, 'block')

    def _expand_block(self, configobj, S=None):
        if S is None:
            S = list()
        S.append(configobj)
        for child in configobj._children:
            if child in S:
                continue
            self._expand_block(child, S)
        return S

    def _diff_line(self, other):
        updates = list()
        for item in self.items:
            if item not in other:
                updates.append(item)
        return updates

    def _diff_strict(self, other):
        updates = list()
        for index, line in enumerate(self.items):
            try:
                if str(line).strip() != str(other[index]).strip():
                    updates.append(line)
            except (AttributeError, IndexError):
                updates.append(line)
        return updates

    def _diff_exact(self, other):
        updates = list()
        if len(other) != len(self.items):
            updates.extend(self.items)
        else:
            for ours, theirs in zip(self.items, other):
                if ours != theirs:
                    updates.extend(self.items)
                    break
        return updates

    def difference(self, other, match='line', path=None, replace=None):
        """Perform a config diff against the another network config

        :param other: instance of NetworkConfig to diff against
        :param match: type of diff to perform.  valid values are 'line',
            'strict', 'exact'
        :param path: context in the network config to filter the diff
        :param replace: the method used to generate the replacement lines.
            valid values are 'block', 'line'

        :returns: a string of lines that are different
        """
        if path and match != 'line':
            try:
                other = other.get_block(path)
            except ValueError:
                other = list()
        else:
            other = other.items

        # generate a list of ConfigLines that aren't in other
        meth = getattr(self, '_diff_%s' % match)
        updates = meth(other)

        if replace == 'block':
            parents = list()
            for item in updates:
                if not item.has_parents:
                    parents.append(item)
                else:
                    for p in item._parents:
                        if p not in parents:
                            parents.append(p)

            updates = list()
            for item in parents:
                updates.extend(self._expand_block(item))

        visited = set()
        expanded = list()

        for item in updates:
            for p in item._parents:
                if p.line not in visited:
                    visited.add(p.line)
                    expanded.append(p)
            expanded.append(item)
            visited.add(item.line)

        return expanded

    def add(self, lines, parents=None):
        ancestors = list()
        offset = 0
        obj = None

        ## global config command
        if not parents:
            for line in lines:
                item = ConfigLine(line)
                item.raw = line
                if item not in self.items:
                    self.items.append(item)

        else:
            for index, p in enumerate(parents):
                try:
                    i = index + 1
                    obj = self.get_block(parents[:i])[0]
                    ancestors.append(obj)

                except ValueError:
                    # add parent to config
                    offset = index * self._indent
                    obj = ConfigLine(p)
                    obj.raw = p.rjust(len(p) + offset)
                    if ancestors:
                        obj._parents = list(ancestors)
                        ancestors[-1]._children.append(obj)
                    self.items.append(obj)
                    ancestors.append(obj)

            # add child objects
            for line in lines:
                # check if child already exists
                for child in ancestors[-1]._children:
                    if child.text == line:
                        break
                else:
                    offset = len(parents) * self._indent
                    item = ConfigLine(line)
                    item.raw = line.rjust(len(line) + offset)
                    item._parents = ancestors
                    ancestors[-1]._children.append(item)
                    self.items.append(item)


class CustomNetworkConfig(NetworkConfig):
    """ custom impl for backwards compat with nxos_* modules """

    def expand_section(self, configobj, S=None):
        if S is None:
            S = list()
        S.append(configobj)
        for child in configobj.children:
            if child in S:
                continue
            self.expand_section(child, S)
        return S

    def get_object(self, path):
        for item in self.items:
            if item.text == path[-1]:
                parents = [p.text for p in item.parents]
                if parents == path[:-1]:
                    return item

    def to_block(self, section):
        return '\n'.join([item.raw for item in section])

    def get_section(self, path):
        try:
            section = self.get_section_objects(path)
            return self.to_block(section)
        except ValueError:
            return list()

    def get_section_objects(self, path):
        if not isinstance(path, list):
            path = [path]
        obj = self.get_object(path)
        if not obj:
            raise ValueError('path does not exist in config')
        return self.expand_section(obj)


    def add(self, lines, parents=None):
        """Adds one or lines of configuration
        """

        ancestors = list()
        offset = 0
        obj = None

        ## global config command
        if not parents:
            for line in to_list(lines):
                item = ConfigLine(line)
                item.raw = line
                if item not in self.items:
                    self.items.append(item)

        else:
            for index, p in enumerate(parents):
                try:
                    i = index + 1
                    obj = self.get_section_objects(parents[:i])[0]
                    ancestors.append(obj)

                except ValueError:
                    # add parent to config
                    offset = index * self.indent
                    obj = ConfigLine(p)
                    obj.raw = p.rjust(len(p) + offset)
                    if ancestors:
                        obj.parents = list(ancestors)
                        ancestors[-1].children.append(obj)
                    self.items.append(obj)
                    ancestors.append(obj)

            # add child objects
            for line in to_list(lines):
                # check if child already exists
                for child in ancestors[-1].children:
                    if child.text == line:
                        break
                else:
                    offset = len(parents) * self.indent
                    item = ConfigLine(line)
                    item.raw = line.rjust(len(line) + offset)
                    item.parents = ancestors
                    ancestors[-1].children.append(item)
                    self.items.append(item)

