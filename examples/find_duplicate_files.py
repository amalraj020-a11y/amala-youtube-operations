"""Report byte-identical files in one folder without changing them."""
from __future__ import annotations

import argparse
import filecmp
import hashlib
from collections import defaultdict
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def duplicate_groups(folder: Path) -> list[list[Path]]:
    if not folder.is_dir():
        raise ValueError(f"Not a folder: {folder}")
    by_size: dict[int, list[Path]] = defaultdict(list)
    for path in folder.iterdir():
        if path.is_file():
            by_size[path.stat().st_size].append(path)
    result = []
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        by_hash: dict[str, list[Path]] = defaultdict(list)
        for path in same_size:
            by_hash[digest(path)].append(path)
        for same_hash in by_hash.values():
            if len(same_hash) < 2:
                continue
            first, *rest = same_hash
            confirmed = [path for path in rest if filecmp.cmp(first, path, shallow=False)]
            if confirmed:
                result.append([first, *confirmed])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Folder to inspect")
    args = parser.parse_args()
    groups = duplicate_groups(args.folder)
    if not groups:
        print("No duplicate files found in this folder.")
    for group in groups:
        print("MATCH:", " = ".join(path.name for path in group))


if __name__ == "__main__":
    main()
