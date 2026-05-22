import hashlib
import sys
from pathlib import Path


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    except PermissionError:
        return "PERMISSION_DENIED"

    except FileNotFoundError:
        return "FILE_NOT_FOUND"


def scan_directory(directory):
    directory_path = Path(directory)

    if not directory_path.exists():
        print("[!] Directory does not exist.")
        return

    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            file_hash = calculate_hash(file_path)
            print(f"{file_path} | {file_hash}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 src/fim.py <directory_to_scan>")
        sys.exit(1)

    scan_directory(sys.argv[1])