# tarpeek

Summarize the contents of a tar archive without extracting it.

`tarpeek` reads only the archive's member metadata (name, type, size,
modification time) and never writes anything to disk — no temp files, no
extraction.

## Install

From the project directory:

```bash
pip install .
```

This installs the `tarpeek` command on your `PATH`, so it can be run from any
directory. For local development, install in editable mode instead:

```bash
pip install -e .
```

## Usage

```bash
tarpeek path/to/archive.tar
```

Example output:

```
NAME          TYPE     SIZE  MODIFIED
big.bin       file     1000  2023-11-14 22:13:20
link_to_big   symlink  0     2023-11-14 22:15:00
some_dir      dir      0     2023-11-14 22:16:40
small.txt     file     2     2023-11-14 22:15:00
```

Members are sorted by size, largest first. Compressed archives (`.tar.gz`,
`.tar.bz2`, `.tar.xz`) are supported automatically.

### Filter by minimum size

```bash
tarpeek path/to/archive.tar --min-size 1024
```

Only members with a size greater than or equal to `BYTES` are shown.

### JSON output

```bash
tarpeek path/to/archive.tar --json
```

Prints a JSON array of objects with `name`, `type`, `size`, and `modified`
fields, in the same sorted/filtered order as the table output.

## Errors

`tarpeek` exits with a non-zero status and prints a message to stderr when:

- the path does not exist
- the path is not a valid tar archive
- the archive contains no members (empty archive)

## Running tests

```bash
pip install -e ".[dev]"
pytest
```

(or simply `pip install pytest && pytest` if you don't need an editable
install).
