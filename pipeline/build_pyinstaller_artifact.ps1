$ErrorActionPreference = "Stop"

pip install --upgrade pip
pip install --upgrade hatch

hatch run codebuild-installer:build
hatch run codebuild-installer:make_exe