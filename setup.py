import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from ansible.release import __version__, __author__
try:
    from setuptools import setup, find_packages
except ImportError:
    print("Ansible now needs setuptools in order to build. Install it using"
            " your package manager (usually python-setuptools) or via pip (pip"
            " install setuptools).")
    sys.exit(1)

with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()
    if not install_requirements:
        print("Unable to read requirements from the requirements.txt file"
                "That indicates this copy of the source code is incomplete.")
        sys.exit(2)

# Python's zipfile does not properly resolve symlinks in the zipfile. When
# installing from zipfile, this can cause malformed versions of the CLI scripts.
path_to_test = os.path.join(os.getcwd(), 'bin', 'ansible-playbook')
# If pulling from VCS and not something run through sdist, it will be a symlink
path_to_test = os.path.realpath(path_to_test)
starts_with_shebang = open(path_to_test, 'r').read(2) == '#!'
if not starts_with_shebang:
    print("It appears that you are installing Ansible from a .zip file. "
          "Because Python's zipfile library does not properly handle symbolic "
          "links in a .zip file, pip and setuptools cannot install Ansible "
          "like this.\n\n")
    print("Please either unzip the .zip file yourself and try again with the "
          "uncompressed version, or install Ansible with pip or setuptools "
          "using the versions on PyPI or directly from the git repository.\n")
    sys.exit(3)

setup(
    name='ansible',
    version=__version__,
    description='Radically simple IT automation',
    author=__author__,
    author_email='info@ansible.com',
    url='https://ansible.com/',
    license='GPLv3',
    # Ansible will also make use of a system copy of python-six and
    # python-selectors2 if installed but use a Bundled copy if it's not.
    install_requires=install_requirements,
    package_dir={ '': 'lib' },
    packages=find_packages('lib'),
    package_data={
        '': [
            'module_utils/*.ps1',
            'modules/windows/*.ps1',
            'modules/windows/*.ps1',
            'galaxy/data/*/*.*',
            'galaxy/data/*/*/*.*',
            'galaxy/data/*/tests/inventory'
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    scripts=[
        'bin/ansible',
        'bin/ansible-playbook',
        'bin/ansible-pull',
        'bin/ansible-doc',
        'bin/ansible-galaxy',
        'bin/ansible-console',
        'bin/ansible-connection',
        'bin/ansible-vault',
    ],
    data_files=[],
)
