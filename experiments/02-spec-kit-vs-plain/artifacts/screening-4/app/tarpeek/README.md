# tarpeek

Summarize the contents of a tar archive without extracting it.

`tarpeek` reads only the member headers of a tar file (name, type, size,
modification time) - it never extracts file contents and never writes
anything to disk.

## Install

From the project directory:

```bash
pip install .
```

or, for an editable install while developing:

```bash
pip install -e .
```

Either way, `pip` installs a `tarpeek` executable onto your `PATH`, so the
command works from any directory afterwards.

## Usage

```bash
tarpeek path/to/archive.tar
```

Example output:

```
NAME             TYPE     SIZE  MODIFIED
docs/big.txt     file     1000  2026-08-17 10:00:00
docs/small.txt   file       10  2026-08-17 10:00:00
docs             dir         0  2026-08-17 10:00:00
link_to_big      symlink     0  2026-08-17 10:00:00
```

Rows are always sorted by size, largest first.

### Filter by minimum size

```bash
tarpeek path/to/archive.tar --min-size 1024
```

Only members with size >= 1024 bytes are shown.

### Machine-readable output

```bash
tarpeek path/to/archive.tar --json
```

Prints a JSON array of objects with `name`, `type`, `size`, and `mtime`
fields, in the same size-descending order as the table.

## Supported archive formats

Anything Python's `tarfile` module can open in read mode, including
uncompressed tar and gzip/bzip2/xz-compressed tar (`.tar`, `.tar.gz`,
`.tgz`, `.tar.bz2`, `.tar.xz`).

## Errors

`tarpeek` exits with a non-zero status and prints a message to stderr for:

- A path that doesn't exist.
- A path that isn't a valid tar archive.
- An archive that contains no members at all.
- A negative `--min-size` value.

Filtering with `--min-size` down to zero matching members is not an error;
it just prints an empty table (or `[]` for `--json`).

## Development

Run the test suite:

```bash
pip install -e ".[test]"
pytest
```
