"""List the largest files in a folder without changing them."""
from __future__ import annotations

import argparse
from pathlib import Path


def largest_files(folder: Path, limit: int = 5) -> list[Path]:
    if not folder.is_dir():
        raise ValueError(f"Not a folder: {folder}")
    files = (entry for entry in folder.iterdir() if entry.is_file())
    return sorted(files, key=lambda entry: entry.stat().st_size, reverse=True)[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Folder to inspect")
    args = parser.parse_args()
    for path in largest_files(args.folder):
        size_mb = path.stat().st_size / 1_048_576
        print(f"{size_mb:8.1f} MB  {path.name}")


if __name__ == "__main__":
    main()
