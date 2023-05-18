#!/usr/bin/env python

import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('duration', type=int)
parser.add_argument('command', nargs='+')
args = parser.parse_args()

try:
    p = subprocess.run(
        ' '.join(args.command),
        shell=True,
        timeout=args.duration,
    )
    sys.exit(p.returncode)
except subprocess.TimeoutExpired:
    sys.exit(124)