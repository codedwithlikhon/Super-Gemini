import os

def write(path: str, content: str):
    """
    Writes content to a file. Creates parent directories if they don't exist.

    Args:
        path (str): The full path to the file.
        content (str): The content to write to the file.

    Returns:
        A success or error message string.
    """
    try:
        # Ensure the directory for the file exists.
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        success_message = f"✅ Successfully wrote {len(content)} bytes to {path}"
        print(success_message)
        return success_message
    except Exception as e:
        error_message = f"❌ Error writing to file {path}: {e}"
        print(error_message)
        return error_message

def read(path: str) -> str:
    """
    Reads and returns the content of a file.

    Args:
        path (str): The path to the file.

    Returns:
        The content of the file as a string, or an error message.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"❌ Error: File not found at {path}"
    except Exception as e:
        return f"❌ Error reading file {path}: {e}"

def list(path: str) -> list[str]:
    """
    Lists the files and directories at a given path.

    Args:
        path (str): The path to the directory.

    Returns:
        A list of file and directory names, or a list with an error message.
    """
    try:
        return os.listdir(path)
    except FileNotFoundError:
        return [f"❌ Error: Directory not found at {path}"]
    except Exception as e:
        return [f"❌ Error listing directory {path}: {e}"]
