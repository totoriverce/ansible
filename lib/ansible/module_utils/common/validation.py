# -*- coding: utf-8 -*-
# Copyright (c) 2018 Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.common.collections import is_iterable


def count_terms(check, params):
    """Count the number of occurrences of a key in a given dictionary

    :arg check: String or iterable of values to check
    :arg params: Dictionary of module parameters

    :returns: An integer that is the number of occurrences of the check values
        in the provided dictionary.
    """

    if not is_iterable(check):
        check = [check]

    return len(set(check).intersection(params))


def check_mutually_exclusive(terms, module_parameters):
    """Check mutually exclusive terms against argument parameters. Accepts
    a single list or list of lists that are groups of terms that should be
    mutually exclusive with one another.

    :arg terms: List of mutually exclusive module parameters
    :arg params: Dictionary of module parameters

    :returns: A list of terms that are mutually exclusive.
    """

    if terms is None:
        return

    result = []
    for check in terms:
        count = count_terms(check, params)
        if count > 1:
            result.append(check)

    return result
