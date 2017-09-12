# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2012-17 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: template
    author: Michael DeHaan <michael.dehaan@gmail.com>
    version_added: "0.9"
    short_description: retrieve contents of file after templating with Jinja2
    description:
      - this is mostly a noop, to be used as a with_list loop when you dont want the content transformed in any way.
    options:
      _terms:
        description: list of files to template
"""

EXAMPLES= """
- name: show templating results
  debug: msg="{{ lookup('template', './some_template.j2') }}
"""

RETURN= """
_raw:
   description: file(s) content after templating
"""

import os

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_bytes, to_text
from ansible.template import generate_ansible_template_vars

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        convert_data_p = kwargs.get('convert_data', True)
        lookup_template_vars = kwargs.get('template_vars', {})
        ret = []

        for term in terms:
            display.debug("File lookup term: %s" % term)

            lookupfile = self.find_file_in_search_path(variables, 'templates', term)
            display.vvvv("File lookup using %s as file" % lookupfile)
            if lookupfile:
                with open(to_bytes(lookupfile, errors='surrogate_or_strict'), 'rb') as f:
                    template_data = to_text(f.read(), errors='surrogate_or_strict')

                    # set jinja2 internal search path for includes
                    searchpath = variables.get('ansible_search_path')
                    if searchpath:
                        # our search paths aren't actually the proper ones for jinja includes.
                        # We want to search into the 'templates' subdir of each search path in
                        # addition to our original search paths.
                        newsearchpath = []
                        for p in searchpath:
                            newsearchpath.append(os.path.join(p, 'templates'))
                            newsearchpath.append(p)
                        searchpath = newsearchpath
                    else:
                        searchpath = [self._loader._basedir, os.path.dirname(lookupfile)]
                    self._templar.environment.loader.searchpath = searchpath

                    # The template will have access to all existing variables,
                    # plus some added by ansible (e.g., template_{path,mtime}),
                    # plus anything passed to the lookup with the template_vars=
                    # argument.
                    vars = variables.copy()
                    vars.update(generate_ansible_template_vars(lookupfile))
                    vars.update(lookup_template_vars)
                    self._templar.set_available_variables(vars)

                    # do the templating
                    res = self._templar.template(template_data, preserve_trailing_newlines=True,
                                                 convert_data=convert_data_p, escape_backslashes=False)
                    ret.append(res)
            else:
                raise AnsibleError("the template file %s could not be found for the lookup" % term)

        return ret
