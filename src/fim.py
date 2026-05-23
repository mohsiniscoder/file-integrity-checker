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

    Path("data").mkdir(exist_ok=True)

    with open(BASELINE_FILE, "w") as file:
        json.dump(baseline, file, indent=4)

    print("[+] Baseline created successfully.")
    print(f"[+] Total files recorded: {len(scan_results)}")
    print(f"[+] Saved to: {BASELINE_FILE}")


def load_baseline():
    baseline_path = Path(BASELINE_FILE)

    if not baseline_path.exists():
        print("[!] No baseline found.")
        print("[!] Run this first:")
        print("    python3 src/fim.py baseline <directory>")
        return None

    with open(BASELINE_FILE, "r") as file:
        return json.load(file)


def check_integrity(directory):
    baseline = load_baseline()

    if baseline is None:
        return

    old_files = baseline["files"]
    current_files = scan_directory(directory)

    if current_files is None:
        return

    modified_files = []
    deleted_files = []
    new_files = []

    for file_path, old_hash in old_files.items():
        if file_path not in current_files:
            deleted_files.append(file_path)
        elif current_files[file_path] != old_hash:
            modified_files.append(file_path)

    for file_path in current_files:
        if file_path not in old_files:
            new_files.append(file_path)

    print("\n===== File Integrity Check Report =====")
    print(f"Checked at: {datetime.now().isoformat()}")
    print(f"Directory: {directory}")

    print("\n[MODIFIED FILES]")
    if modified_files:
        for file in modified_files:
            print(f"  [!] {file}")
    else:
        print("  None")

    print("\n[DELETED FILES]")
    if deleted_files:
        for file in deleted_files:
            print(f"  [-] {file}")
    else:
        print("  None")

    print("\n[NEW FILES]")
    if new_files:
        for file in new_files:
            print(f"  [+] {file}")
    else:
        print("  None")

    print("\n=======================================")


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python3 src/fim.py baseline <directory>")
        print("  python3 src/fim.py check <directory>")
        sys.exit(1)

    command = sys.argv[1]
    directory = sys.argv[2]

    if command == "baseline":
        create_baseline(directory)
    elif command == "check":
        check_integrity(directory)
    else:
        print("[!] Unknown command.")
        print("Available commands: baseline, check")


if __name__ == "__main__":
    main()