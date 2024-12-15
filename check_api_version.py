#!/usr/bin/env python3

import re
import subprocess
from pathlib import Path

SETTINGS_FILE = Path("django/unnamed_webapp/settings.py")
PYPROJECT_FILE = Path("django/pyproject.toml")
VERSION_PATTERN = r"^\d+\.\d+\.\d{3}(-dev\d+)?$"


def validate_version(version_string):
    if not re.match(VERSION_PATTERN, version_string):
        raise ValueError(f"Invalid version format: {version_string}. " f"Expected format: 0.1.903 or 0.1.903-dev1")


def get_current_version():
    with open(PYPROJECT_FILE) as file:
        for line in file:
            if line.strip().startswith("version = "):
                return line.split("=")[1].strip().strip('"')

    raise ValueError("Version not found in pyproject.toml")


def get_previous_version():
    try:
        result = subprocess.run(
            ["git", "show", "HEAD:django/pyproject.toml"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.strip().startswith("version = "):
                return line.split("=")[1].strip().strip('"')
    except subprocess.CalledProcessError:
        return None

    return None


def check_api_version():
    try:
        current_version = get_current_version()
        validate_version(current_version)

        previous_version = get_previous_version()

        if previous_version is None:
            print("Unable to retrieve previous version. This might be the initial commit.")
            return 0

        if current_version == previous_version:
            print(f"Warning: API version has not changed. Current version: {current_version}")
            return 1
        else:
            print(f"API version has been updated. Previous: {previous_version}, Current: {current_version}")
            return 0

    except ValueError as e:
        print(f"Error: {e}")
        return 1


def main():
    return check_api_version()


if __name__ == "__main__":
    exit(main())
