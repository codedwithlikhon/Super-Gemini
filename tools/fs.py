import os

class FileSystem:
    """
    A tool for interacting with the filesystem.
    """
    def read_file(self, path: str) -> str:
        print(f"Reading file: {path}")
        with open(path, 'r') as f:
            return f.read()

    def write_file(self, path: str, content: str):
        print(f"Writing to file: {path}")
        with open(path, 'w') as f:
            f.write(content)

    def list_dir(self, path: str) -> list:
        print(f"Listing directory: {path}")
        return os.listdir(path)
