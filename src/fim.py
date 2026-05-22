import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime


BASELINE_FILE = "data/baseline.json"


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
    scan_results = {}

    if not directory_path.exists():
        print("[!] Directory does not exist.")
        return None

    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            file_hash = calculate_hash(file_path)
            scan_results[str(file_path)] = file_hash

    return scan_results


def create_baseline(directory):
    scan_results = scan_directory(directory)

    if scan_results is None:
        return

    baseline = {
        "created_at": datetime.now().isoformat(),
        "directory": directory,
        "files": scan_results
    }

    with open(BASELINE_FILE, "w") as file:
        json.dump(baseline, file, indent=4)

    print(f"[+] Baseline created successfully.")
    print(f"[+] Total files recorded: {len(scan_results)}")
    print(f"[+] Saved to: {BASELINE_FILE}")


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python3 src/fim.py baseline <directory>")
        sys.exit(1)

    command = sys.argv[1]
    directory = sys.argv[2]

    if command == "baseline":
        create_baseline(directory)
    else:
        print("[!] Unknown command.")
        print("Available command: baseline")


if __name__ == "__main__":
    main()