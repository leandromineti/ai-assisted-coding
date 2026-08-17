import sys
import argparse
from .core import read_tar_members, format_table, format_json, TarArchiveError


def main():
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Summarize tar archive contents without extracting",
    )
    parser.add_argument("archive", help="Path to the tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=0,
        help="Minimum size in bytes to include (default: 0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    try:
        members = read_tar_members(args.archive, min_size=args.min_size)

        if args.json:
            output = format_json(members)
        else:
            output = format_table(members)

        print(output)
        sys.exit(0)

    except TarArchiveError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
