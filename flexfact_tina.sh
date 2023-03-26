#!/usr/bin/env bash

# This script is a helper to easily call
# the main.py file with a python interpreter
root_dir="$(dirname "$0")"
/usr/bin/env python3 -B $root_dir/src/main.py "$@"
