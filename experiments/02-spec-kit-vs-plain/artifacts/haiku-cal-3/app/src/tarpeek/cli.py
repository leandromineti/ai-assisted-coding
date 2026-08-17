import sys
import json
import argparse
from typing import List
from tabulate import tabulate

from .core import ArchiveReader, TarMember, TarPeekError


def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            if size == int(size):
                return f"{int(size)}{unit}"
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def print_table(members: List[TarMember]) -> None:
    headers = ["Name", "Type", "Size (bytes)", "Size", "Modified"]
    rows = [
        [
            member.name,
            member.type,
            member.size,
            format_size(member.size),
            member.modified,
        ]
        for member in members
    ]
    print(tabulate(rows, headers=headers, tablefmt="grid"))


def print_json(members: List[TarMember]) -> None:
    data = [member.to_dict() for member in members]
    print(json.dumps(data, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='tarpeek',
        description='Summarize tar archive contents without extracting',
    )
    parser.add_argument(
        'archive',
        help='Path to tar archive',
    )
    parser.add_argument(
        '--min-size',
        type=int,
        default=0,
        help='Filter members by minimum size in bytes (default: 0)',
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON instead of table',
    )

    args = parser.parse_args()

    try:
        reader = ArchiveReader(args.archive)
        members = reader.read_members(min_size=args.min_size)
        members = reader.sort_by_size(members)

        if args.json:
            print_json(members)
        else:
            print_table(members)

        return 0

    except TarPeekError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
