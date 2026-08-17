import sys
import argparse
from datetime import datetime, timezone
from tabulate import tabulate
from tarpeek.archive import TarArchive


def format_date(timestamp: int) -> str:
    """Format unix timestamp as ISO date string."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def print_table(archive: TarArchive, min_size: int = 0) -> None:
    """Print members as a formatted table."""
    members = archive.filter_by_min_size(min_size)
    if not members:
        print("No members found.", file=sys.stderr)
        sys.exit(1)

    members = archive.sort_by_size(members)

    rows = []
    for member in members:
        rows.append([
            member.name,
            member.type,
            member.size,
            format_date(member.mtime),
        ])

    headers = ["Name", "Type", "Size (bytes)", "Last-Modified"]
    print(tabulate(rows, headers=headers, tablefmt="simple"))


def print_json(archive: TarArchive, min_size: int = 0) -> None:
    """Print members as JSON."""
    members = archive.filter_by_min_size(min_size)
    if not members:
        print("[]")
        return
    members = archive.sort_by_size(members)
    print(archive.to_json(members))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize tar archive contents without extracting"
    )
    parser.add_argument("archive", help="Path to tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=0,
        help="Filter members with size >= BYTES (default: 0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    try:
        archive = TarArchive(args.archive)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not archive.members:
        print("Error: Archive is empty", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print_json(archive, args.min_size)
    else:
        print_table(archive, args.min_size)


if __name__ == "__main__":
    main()
