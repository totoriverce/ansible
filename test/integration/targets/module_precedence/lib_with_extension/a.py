#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json


def main():
    print(json.dumps(dict(changed=False, location='a.py')))


if __name__ == '__main__':
    main()
