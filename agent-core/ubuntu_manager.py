import subprocess
import os

def is_ubuntu_installed():
    """
    Checks if the proot-distro Ubuntu environment has been installed.
    It does this by running `proot-distro list` and checking for 'ubuntu'.
    """
    try:
        result = subprocess.run(
            ['proot-distro', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        # The output lists installed distributions. We just check if 'ubuntu' is mentioned.
        return 'ubuntu' in result.stdout.lower()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If proot-distro is not found or the command fails, we assume not installed.
        print("Warning: 'proot-distro' command not found or failed. Assuming Ubuntu is not installed.")
        return False

def execute_in_ubuntu(command: str, as_root: bool = True):
    """
    Executes a given command inside the proot-distro Ubuntu environment.

    Args:
        command: The command string to execute inside Ubuntu.
        as_root: Whether to run the command as the root user (default).

    Returns:
        The subprocess result object.
    """
    print(f"Executing in Ubuntu: `{command}`")
    try:
        # Construct the command array for subprocess
        # The '--' is crucial to separate proot-distro's args from the command.
        proot_command = ['proot-distro', 'exec', 'ubuntu']
        if not as_root:
            # proot-distro exec --user <user> ...
            # We assume a non-root user would need to be created separately.
            # For now, we'll just show how it could be done.
            # Let's stick to root for simplicity unless specified.
            pass

        proot_command.extend(['--', '/bin/bash', '-c', command])

        result = subprocess.run(proot_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error executing command in Ubuntu. Stderr:\n{result.stderr}")

        return result
    except FileNotFoundError:
        print("Error: 'proot-distro' command not found. Cannot execute in Ubuntu.")
        return None
