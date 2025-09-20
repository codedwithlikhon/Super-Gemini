import subprocess

def is_ubuntu_installed():
    """
    Checks if the proot-distro Ubuntu environment has been installed.
    """
    try:
        result = subprocess.run(
            ['proot-distro', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        return 'ubuntu' in result.stdout.lower()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: 'proot-distro' command not found or failed. Assuming Ubuntu is not installed.")
        return False

def execute_in_ubuntu(command: str):
    """
    Executes a given command inside the proot-distro Ubuntu environment.
    """
    print(f"Executing in Ubuntu: `{command}`")
    try:
        proot_command = ['proot-distro', 'exec', 'ubuntu', '--', '/bin/bash', '-c', command]
        result = subprocess.run(proot_command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing command in Ubuntu. Stderr:\n{result.stderr}")
        return result
    except FileNotFoundError:
        print("Error: 'proot-distro' command not found. Cannot execute in Ubuntu.")
        return None
