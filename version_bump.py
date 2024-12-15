#!/usr/bin/env python3

import re
import subprocess
from pathlib import Path

SETTINGS_FILE = Path("api/djongo/settings.py")
PYPROJECT_FILE = Path("api/pyproject.toml")
VERSION_PATTERN = r"^\d+\.\d+\.\d+(-dev\d+)?$"


def validate_version(version_string):
    if not re.match(VERSION_PATTERN, version_string):
        raise ValueError(f"Invalid version format: {version_string}. " f"Expected format: 0.1.90 or 0.1.90-dev1")


def bump_version(version_string):
    validate_version(version_string)
    base_version = version_string.split("-")[0]  # Remove dev suffix if present
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", base_version)
    major, minor, patch = map(int, match.groups())

    patch += 1
    if patch > 99:
        minor += 1
        patch = 0
    if minor > 99:
        major += 1
        minor = 0

    new_version = f"{major}.{minor}.{patch:02d}"

    # Preserve dev suffix if it existed
    if "-dev" in version_string:
        dev_match = re.search(r"-dev(\d+)", version_string)
        if dev_match:
            new_version += f"-dev{dev_match.group(1)}"

    return new_version


def update_version_in_settings(new_version):
    with open(SETTINGS_FILE) as file:
        content = file.read()

    pattern = r'API_VERSION\s*=\s*["\'](.+?)["\']'
    if re.search(pattern, content):
        updated_content = re.sub(pattern, lambda m: f'API_VERSION = "{new_version}"', content)
    else:
        updated_content = content + f'\n\nAPI_VERSION = "{new_version}"\n'

    with open(SETTINGS_FILE, "w") as file:
        file.write(updated_content)


def update_version_in_pyproject(new_version):
    with open(PYPROJECT_FILE) as file:
        content = file.readlines()

    for i, line in enumerate(content):
        if line.strip().startswith("version = "):
            content[i] = f'version = "{new_version}"\n'
            break
    else:
        raise ValueError("Version field not found in pyproject.toml")

    with open(PYPROJECT_FILE, "w") as file:
        file.writelines(content)


def get_current_version():
    with open(PYPROJECT_FILE) as file:
        for line in file:
            if line.strip().startswith("version = "):
                return line.split("=")[1].strip().strip('"')

    raise ValueError("Version not found in pyproject.toml")


def main():
    try:
        current_version = get_current_version()
        validate_version(current_version)
        new_version = bump_version(current_version)

        update_version_in_settings(new_version)
        update_version_in_pyproject(new_version)

        print(f"Bumped version from {current_version} to {new_version}")
        print(f"Updated {SETTINGS_FILE} and {PYPROJECT_FILE}")

        # Stage the updated files
        subprocess.run(["git", "add", str(SETTINGS_FILE), str(PYPROJECT_FILE)])

        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
