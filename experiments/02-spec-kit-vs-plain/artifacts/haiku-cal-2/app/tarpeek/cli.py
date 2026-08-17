#!/usr/bin/env python
import argparse
import json
import sys
import tarfile
from datetime import datetime
from pathlib import Path


def format_size(size_bytes):
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def get_member_type(member):
    """Return member type as string."""
    if member.issym():
        return "symlink"
    elif member.isdir():
        return "dir"
    else:
        return "file"


def summarize_archive(archive_path, min_size=None):
    """
    Summarize tar archive contents.

    Returns list of dicts with: name, type, size, modified
    Raises ValueError if not a valid tar or is empty.
    """
    archive_path = Path(archive_path)

    if not archive_path.exists():
        raise FileNotFoundError(f"File not found: {archive_path}")

    try:
        with tarfile.open(archive_path, "r:*") as tar:
            members = tar.getmembers()

            if not members:
                raise ValueError("Archive is empty")

            results = []
            for member in members:
                if min_size is not None and member.size < min_size:
                    continue

                results.append({
                    "name": member.name,
                    "type": get_member_type(member),
                    "size": member.size,
                    "modified": datetime.fromtimestamp(member.mtime).isoformat(),
                })

            # Sort by size descending
            results.sort(key=lambda x: x["size"], reverse=True)
            return results

    except tarfile.TarError as e:
        raise ValueError(f"Not a valid tar archive: {e}")


def format_table(members):
    """Format members as ASCII table."""
    if not members:
        print("No members match the filter.")
        return

    # Calculate column widths
    name_width = max(len(m["name"]) for m in members) if members else 10
    name_width = max(name_width, 4)  # "Name" header

    type_width = max(len(m["type"]) for m in members) if members else 4
    type_width = max(type_width, 4)  # "Type" header

    size_width = 10  # Max size display
    modified_width = 19  # ISO format "2026-08-17T15:02:00"

    # Print header
    header = f"{'Name':<{name_width}}  {'Type':<{type_width}}  {'Size':<{size_width}}  {'Modified':<{modified_width}}"
    print(header)
    print("-" * len(header))

    # Print rows
    for member in members:
        size_str = f"{member['size']:>8}B"
        print(
            f"{member['name']:<{name_width}}  "
            f"{member['type']:<{type_width}}  "
            f"{size_str:<{size_width}}  "
            f"{member['modified']:<{modified_width}}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Summarize tar archive contents without extracting"
    )
    parser.add_argument("archive", help="Path to tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=None,
        help="Minimum size in bytes to include (default: no filter)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of table",
    )

    args = parser.parse_args()

    try:
        members = summarize_archive(args.archive, min_size=args.min_size)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(members, indent=2))
    else:
        format_table(members)


if __name__ == "__main__":
    main()
