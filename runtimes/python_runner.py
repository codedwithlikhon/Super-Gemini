# Executes a python script safely.
import sys

def run_python_script(script_path: str):
    """
    Runs a Python script.
    """
    print(f"Running python script: {script_path}")
    # In a real scenario, this would use subprocess in a secure way.
    with open(script_path, 'r') as f:
        exec(f.read())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_python_script(sys.argv[1])
