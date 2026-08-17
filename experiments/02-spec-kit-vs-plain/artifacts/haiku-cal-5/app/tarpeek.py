#!/usr/bin/env python3
"""tarpeek: Summarize tar archive contents without extracting."""

import tarfile
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def format_size(size: int) -> str:
    """Format byte size as human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size}{unit}"
        size //= 1024
    return f"{size}TB"


def get_member_type(member: tarfile.TarInfo) -> str:
    """Get human-readable type for tar member."""
    if member.issym() or member.islnk():
        return "symlink"
    elif member.isdir():
        return "dir"
    elif member.isfile():
        return "file"
    else:
        return "other"


def peek_archive(archive_path: str, min_size: int = 0) -> List[Dict[str, Any]]:
    """Extract metadata from tar archive members."""
    members = []

    try:
        with tarfile.open(archive_path, "r:*") as tar:
            for member in tar.getmembers():
                if member.size >= min_size:
                    members.append({
                        "name": member.name,
                        "type": get_member_type(member),
                        "size": member.size,
                        "mtime": datetime.fromtimestamp(member.mtime).isoformat(),
                    })
    except tarfile.ReadError:
        raise ValueError(f"Not a valid tar archive: {archive_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    return members


def print_table(members: List[Dict[str, Any]]) -> None:
    """Print members as formatted table."""
    if not members:
        print("Empty archive.")
        return

    # Column widths
    name_width = max(len(m["name"]) for m in members) if members else 10
    name_width = max(name_width, 10)  # min width for "Name" header

    # Header
    print(f"{'Name':<{name_width}} {'Type':<8} {'Size':>10} {'Last Modified'}")
    print("-" * (name_width + 8 + 12 + 25))

    # Rows
    for member in members:
        size_str = f"{member['size']:>10}"
        print(f"{member['name']:<{name_width}} {member['type']:<8} {size_str} {member['mtime']}")


def print_json(members: List[Dict[str, Any]]) -> None:
    """Print members as JSON."""
    print(json.dumps(members, indent=2))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Summarize tar archive contents without extracting",
        prog="tarpeek"
    )
    parser.add_argument("archive", help="Path to tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=0,
        metavar="BYTES",
        help="Only show members >= this size in bytes"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    try:
        members = peek_archive(args.archive, args.min_size)

        # Sort by size descending
        members.sort(key=lambda m: m["size"], reverse=True)

        if args.json:
            print_json(members)
        else:
            print_table(members)

        return 0

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
