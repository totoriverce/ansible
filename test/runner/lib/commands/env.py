"""Show information about the test environment."""

from __future__ import absolute_import, print_function

import datetime
import json
import os
import platform
import re
import sys

from lib.config import (
    CommonConfig,
)

from lib.util import (
    display,
    raw_command,
    SubprocessError,
    ApplicationError,
)

from lib.ansible_util import (
    ansible_environment,
)

from lib.git import (
    Git,
)

from lib.docker_util import (
    docker_info,
    docker_version
)


class EnvConfig(CommonConfig):
    """Configuration for the tools command."""
    def __init__(self, args):
        """
        :type args: any
        """
        super(EnvConfig, self).__init__(args, 'env')

        self.show = args.show or not args.dump
        self.dump = args.dump


def command_env(args):
    """
    :type args: EnvConfig
    """
    data = dict(
        ansible=dict(
            version=get_ansible_version(args),
        ),
        docker=get_docker_details(args),
        environ=os.environ.copy(),
        git=get_git_details(args),
        platform=dict(
            datetime=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            platform=platform.platform(),
            uname=platform.uname(),
        ),
        python=dict(
            executable=sys.executable,
            version=platform.python_version(),
        ),
    )

    if args.show:
        verbose = {
            'docker': 3,
            'environ': 2,
            'platform.uname': 1,
        }

        show_dict(data, verbose)

    if args.dump and not args.explain:
        with open('test/results/bot/data-environment.json', 'w') as results_fd:
            results_fd.write(json.dumps(data, sort_keys=True))


def show_dict(data, verbose, root_verbosity=0, path=None):
    """
    :type data: dict[str, any]
    :type verbose: dict[str, int]
    :type root_verbosity: int
    :type path: list[str] | None
    """
    path = path if path else []

    for key, value in sorted(data.items()):
        indent = '  ' * len(path)
        key_path = path + [key]
        key_name = '.'.join(key_path)
        verbosity = verbose.get(key_name, root_verbosity)

        if isinstance(value, (tuple, list)):
            display.info(indent + '%s:' % key, verbosity=verbosity)
            for item in value:
                display.info(indent + '  - %s' % item, verbosity=verbosity)
        elif isinstance(value, dict):
            display.info(indent + '%s:' % key, verbosity=verbosity)
            show_dict(value, verbose, verbosity, key_path)
        else:
            display.info(indent + '%s: %s' % (key, value), verbosity=verbosity)


def get_ansible_version(args):
    """
    :type args: CommonConfig
    :rtype: str | None
    """
    code = 'from __future__ import (print_function); from ansible.release import __version__; print(__version__)'
    cmd = [sys.executable, '-c', code]
    env = ansible_environment(args)

    try:
        ansible_version, _dummy = raw_command(cmd, env=env, capture=True)
        ansible_version = ansible_version.strip()
    except SubprocessError:
        ansible_version = None

    return ansible_version


def get_docker_details(args):
    """
    :type args: CommonConfig
    :rtype: dict[str, any]
    """
    try:
        info = docker_info(args)
    except ApplicationError:
        info = None

    try:
        version = docker_version(args)
    except ApplicationError:
        version = None

    docker_details = dict(
        info=info,
        version=version,
    )

    return docker_details


def get_git_details(args):
    """
    :type args: CommonConfig
    :rtype: dict[str, any]
    """
    commit = os.environ.get('COMMIT')
    base_commit = os.environ.get('BASE_COMMIT')

    git_details = dict(
        base_commit=base_commit,
        commit=commit,
        merged_commit=get_merged_commit(args, commit),
        root=os.getcwd(),
    )

    return git_details


def get_merged_commit(args, commit):
    """
    :type args: CommonConfig
    :type commit: str
    :rtype: str | None
    """
    if not commit:
        return None

    git = Git(args)

    try:
        show_commit = git.run_git(['show', '--no-patch', '--no-abbrev', commit])
    except SubprocessError as ex:
        # This should only fail for pull requests where the commit does not exist.
        # Merge runs would fail much earlier when attempting to checkout the commit.
        raise ApplicationError('Commit %s was not found:\n\n%s\n\n'
                               'The commit was likely removed by a force push between job creation and execution.\n'
                               'Find the latest run for the pull request and restart failed jobs as needed.'
                               % (commit, ex.stderr.strip()))

    head_commit = git.run_git(['show', '--no-patch', '--no-abbrev', 'HEAD'])

    if show_commit == head_commit:
        # Commit is HEAD, so this is not a pull request or the base branch for the pull request is up-to-date.
        return None

    match_merge = re.search(r'^Merge: (?P<parents>[0-9a-f]{40} [0-9a-f]{40})$', head_commit, flags=re.MULTILINE)

    if not match_merge:
        # The most likely scenarios resulting in a failure here are:
        # A new run should or does supersede this job, but it wasn't cancelled in time.
        # A job was superseded and then later restarted.
        raise ApplicationError('HEAD is not commit %s or a merge commit:\n\n%s\n\n'
                               'This job has likely been superseded by another run due to additional commits being pushed.\n'
                               'Find the latest run for the pull request and restart failed jobs as needed.'
                               % (commit, head_commit.strip()))

    parents = set(match_merge.group('parents').split(' '))

    if len(parents) != 2:
        raise ApplicationError('HEAD is a %d-way octopus merge.' % len(parents))

    if commit not in parents:
        raise ApplicationError('Commit %s is not a parent of HEAD.' % commit)

    parents.remove(commit)

    last_commit = parents.pop()

    return last_commit
