#!/usr/bin/env python3
"""
Consolidate all text-based files under a given directory (recursively)
into a single .txt file, with a header showing each file's path.

Usage:
    python consolidate_files.py
    (then enter the folder path when prompted)
"""

import json
import os
import sys

# History of previously used folder paths, stored alongside this script
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".consolidate_history.json")
MAX_HISTORY = 10

# Folders to skip entirely (junk / non-source dirs)
SKIP_DIRS = {
    "node_modules", ".git", ".svn", "__pycache__", ".venv", "venv",
    "env", "bin", "obj", "dist", "build", ".next", ".idea", ".vscode",
    "target", ".pytest_cache", ".mypy_cache", "coverage", ".sln", "packages",
}

# Extensions we treat as binary/non-text and skip
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so",
    ".pyc", ".class", ".jar", ".mp3", ".mp4", ".mov", ".avi", ".woff",
    ".woff2", ".ttf", ".eot", ".db", ".sqlite", ".bin", ".dat", ".sln"
}


def is_probably_text(filepath, blocksize=1024):
    """Heuristic: read a chunk and check for null bytes / decode errors."""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(blocksize)
        if b"\x00" in chunk:
            return False
        chunk.decode("utf-8", errors="strict")
        return True
    except (UnicodeDecodeError, OSError):
        # Try a more lenient check before giving up
        try:
            with open(filepath, "rb") as f:
                chunk = f.read(blocksize)
            chunk.decode("utf-8", errors="ignore")
            # If it decoded with ignore but had a strict failure above,
            # still treat as text unless there were null bytes.
            return b"\x00" not in chunk
        except OSError:
            return False


def consolidate(root_path, output_path, extra_skip_dirs=None):
    root_path = os.path.abspath(root_path)
    file_count = 0
    skipped_count = 0

    skip_dirs = SKIP_DIRS | (extra_skip_dirs or set())

    with open(output_path, "w", encoding="utf-8") as out:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Prune skip-dirs in place so os.walk doesn't descend into them
            dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith(".")]

            for fname in sorted(filenames):
                fpath = os.path.join(dirpath, fname)
                ext = os.path.splitext(fname)[1].lower()

                if ext in BINARY_EXTS:
                    skipped_count += 1
                    continue

                if not is_probably_text(fpath):
                    skipped_count += 1
                    continue

                rel_path = os.path.relpath(fpath, root_path)

                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except OSError as e:
                    print(f"  Warning: could not read {rel_path}: {e}")
                    skipped_count += 1
                    continue

                out.write("=" * 80 + "\n")
                out.write(f"FILE: {rel_path}\n")
                out.write("=" * 80 + "\n\n")
                out.write(content)
                out.write("\n\n")
                file_count += 1

    return file_count, skipped_count


def load_history():
    if not os.path.isfile(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except OSError as e:
        print(f"  Warning: could not save folder history: {e}")


def add_to_history(history, path):
    path = os.path.abspath(path)
    # Move to front, dedup, cap length
    history = [p for p in history if p != path]
    history.insert(0, path)
    return history[:MAX_HISTORY]


def prompt_for_root_path():
    history = load_history()

    if history:
        print("\nPreviously used folders:")
        for i, path in enumerate(history, start=1):
            print(f"  {i}. {path}")
        print("  0. Enter a new path")

        choice = input("\nSelect a number, or paste a new folder path: ").strip()

        if choice.isdigit():
            idx = int(choice)
            if idx == 0:
                root_path = input("Enter the folder path to consolidate: ").strip().strip('"')
            elif 1 <= idx <= len(history):
                root_path = history[idx - 1]
            else:
                print("Invalid selection.")
                sys.exit(1)
        else:
            root_path = choice.strip('"')
    else:
        root_path = input("Enter the folder path to consolidate: ").strip().strip('"')

    return root_path, history


def main():
    root_path, history = prompt_for_root_path()

    if not os.path.isdir(root_path):
        print(f"Error: '{root_path}' is not a valid directory.")
        sys.exit(1)

    history = add_to_history(history, root_path)
    save_history(history)

    ignore_input = input(
        "Enter folder names to ignore, comma-separated (or press Enter to skip): "
    ).strip()
    extra_skip_dirs = {
        name.strip() for name in ignore_input.split(",") if name.strip()
    } if ignore_input else set()

    default_name = "consolidated_output.txt"
    output_path = os.path.join(os.getcwd(), default_name)

    print(f"\nScanning '{root_path}' recursively...")
    if extra_skip_dirs:
        print(f"  Ignoring folders named: {', '.join(sorted(extra_skip_dirs))}")
    file_count, skipped_count = consolidate(root_path, output_path, extra_skip_dirs)

    print(f"\nDone.")
    print(f"  Files included: {file_count}")
    print(f"  Files skipped (binary/unreadable): {skipped_count}")
    print(f"  Output written to: {output_path}")


if __name__ == "__main__":
    main()