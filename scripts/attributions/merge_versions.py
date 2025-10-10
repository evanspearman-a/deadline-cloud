# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import argparse
import json
import platform
from pathlib import Path

PLATFORM_MAP: dict[str, str] = {
    "Darwin": "osx-installer.app.zip",
    "Windows": "windows-x64-installer.exe",
    "Linux": "linux-x64-installer.run",
}

def merge_versions(
    python_dependencies_file: Path,
    software_versions_file: Path,
    pyinstaller_version_file: Path,
    installer_name: str,
    output_prefix: Path,
) -> None:
    with open(python_dependencies_file, "r") as f:
        python_dependencies = json.load(f)
    with open(software_versions_file, "r") as f:
        software_versions = json.load(f)
    with open(pyinstaller_version_file, "r") as f:
        pyinstaller_version = json.load(f)

    # Some dependencies on macOS just use the version that was on the system at build time.
    # These include zlib, bzip2, tcl, tk, and libffi.
    # We can determine some of the versions at runtime, so we will do that here.
    # This only works if this script is run by the same Python interpreter
    # as is shipped with the pyinstaller build, which is the case in
    # our pipelines.
    # The bzip2 and libffi versions are not exposed by Python
    if platform.system() == "Darwin":
        # Import these here because we don't build with tcl/tk on Linux
        import tkinter
        import zlib

        zlib_version = zlib.ZLIB_VERSION
        tcl_version = tkinter.TclVersion
        tk_version = tkinter.TkVersion

        python_dependencies["zlib"] = zlib_version
        python_dependencies["tcl"] = tcl_version
        python_dependencies["tk"] = tk_version

    combined = {}

    for versions in [software_versions, pyinstaller_version]:
        for name, version in versions.items():
            if name not in combined:
                combined[name] = version
            elif combined[name] != version:
                raise RuntimeError(f"Conflicting versions for {name}: {version}, {combined[name]}")

    result = {
        "python": combined,
        "native": python_dependencies,
    }

    output_file_path = (
        output_prefix / f"{installer_name}-{PLATFORM_MAP[platform.system()]}.dependencies.json"
    )

    with open(output_file_path, "w", encoding="utf8") as f:
        json.dump(result, f)


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python-dependencies-file",
        type=Path,
        required=True,
        help="The path to the python-dependencies.json file",
    )
    parser.add_argument(
        "--software-versions-file",
        type=Path,
        required=True,
        help="The path to the software-versions.json file",
    )
    parser.add_argument(
        "--pyinstaller-version-file",
        type=Path,
        required=True,
        help="The path to the pyinstaller-version.json file",
    )
    parser.add_argument(
        "--installer-name",
        type=str,
        required=True,
        help="The name of the installer, eg. DeadlineCloudClient",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        required=True,
        help="The path to output the merged json to",
    )
    args = parser.parse_args()

    merge_versions(
        args.python_dependencies_file,
        args.software_versions_file,
        args.pyinstaller_version_file,
        args.installer_name,
        args.output_prefix,
    )


if __name__ == "__main__":
    _main()
