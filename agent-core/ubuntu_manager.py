import subprocess

def is_ubuntu_installed():
    """
    Checks if the proot-distro Ubuntu environment has been installed.
    """
    try:
        result = subprocess.run(['proot-distro', 'list'], capture_output=True, text=True, check=True)
        return 'ubuntu' in result.stdout.lower()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def execute_in_ubuntu(command: str):
    """
    Executes a given command inside the proot-distro Ubuntu environment.
    """
    try:
        proot_command = ['proot-distro', 'exec', 'ubuntu', '--', '/bin/bash', '-c', command]
        result = subprocess.run(proot_command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing in Ubuntu: {result.stderr}")
        return result
    except FileNotFoundError:
        print("Error: 'proot-distro' command not found.")
        return None
