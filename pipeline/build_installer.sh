#!/bin/sh
# Set the -e option
set -e

hatch run codebuild-installer:build_installer "$@"