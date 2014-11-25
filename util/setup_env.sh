#!/bin/bash
PROJECT_DIR="$(cd $(dirname $BASH_SOURCE)/..; pwd)"
ENV_DIR="$PROJECT_DIR/python_env"

virtualenv $ENV_DIR \
            --system-site-packages  # needed for samba4
$ENV_DIR/bin/pip install -r "$PROJECT_DIR/requirements.txt"
