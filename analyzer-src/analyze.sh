#!/bin/bash

set -e
CODE_DIR="/analysis/inputs/public/source-code"
THIS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


flake8 --format=json --select=r2c ${CODE_DIR} | python3 ${THIS_SCRIPT_DIR}/formatter.py ${CODE_DIR} > /analysis/output/output.json
