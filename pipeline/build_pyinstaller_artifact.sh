#!/bin/sh
# Set the -e option
set -e

pip install --upgrade pip
pip install --upgrade hatch

hatch run codebuild-installer:build
hatch run codebuild-installer:make_exe