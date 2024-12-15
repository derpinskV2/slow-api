import sys
import toml
from subprocess import check_output, CalledProcessError


def get_file_content(file_path, revision=None):
    if revision:
        try:
            return check_output(["git", "show", f"{revision}:{file_path}"]).decode("utf-8")
        except CalledProcessError as e:
            print(f"Error getting content of {file_path} at {revision}: {e}")
            return ""
    else:
        try:
            with open(file_path) as f:
                return f.read()
        except OSError as e:
            print(f"Error reading {file_path}: {e}")
            return ""


def extract_version(content):
    try:
        config = toml.loads(content)
        version = config["tool"]["poetry"]["version"]
        print(f"Extracted version: {version}")
        return version
    except toml.TomlDecodeError as e:
        print(f"Error decoding TOML: {e}")
        print(f"Content: {content}")
    except KeyError as e:
        print(f"Error accessing version key: {e}")
        print(f"TOML content: {config}")
    return None


def main():
    file_path = "api/pyproject.toml"

    print(f"Checking file: {file_path}")

    current_content = get_file_content(file_path)  # Read current file from disk
    previous_content = get_file_content(file_path, "HEAD")  # Get last committed version

    current_version = extract_version(current_content)
    previous_version = extract_version(previous_content)

    if current_version is None:
        print(f"Error: Couldn't find version in {file_path}")
        sys.exit(1)

    if current_version == previous_version:
        print(f"API version not updated. Current version: {current_version}")
        sys.exit(1)
    else:
        print(f"API version updated from {previous_version} to {current_version}")
        sys.exit(0)


if __name__ == "__main__":
    main()
