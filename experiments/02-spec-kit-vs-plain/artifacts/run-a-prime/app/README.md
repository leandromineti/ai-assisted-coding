# tarpeek

Summarize the contents of a tar archive without extracting it.

`tarpeek` reads a `.tar`, `.tar.gz`/`.tgz`, `.tar.bz2`, or `.tar.xz` archive's
metadata and prints a table of its members — name, type, size, and
last-modified date — sorted by size, largest first. It never writes anything
to the filesystem: it only reads member headers, it never calls `extract()`.

## Install

From the project root:

```bash
pip install .
```

This installs the `tarpeek` command on your `PATH`, so it can be run from any
directory. For development (editable install, so code changes take effect
immediately):

```bash
pip install -e ".[test]"
```

## Usage

```bash
tarpeek ARCHIVE [--min-size BYTES] [--json]
```

- `ARCHIVE` — path to a tar archive (any compression `tarfile` supports).
- `--min-size BYTES` — only show members whose size is at least `BYTES`.
- `--json` — print machine-readable JSON instead of a table.

### Example

```
$ tarpeek release.tar.gz
NAME              TYPE     SIZE   LAST MODIFIED
data/big.bin      file     5000   2026-08-17 18:09:13
data/notes.txt    file     12     2026-08-17 18:09:13
data/link.txt     symlink  0      2026-08-17 18:09:13
data              dir      0      2026-08-17 18:09:13

$ tarpeek release.tar.gz --min-size 1000 --json
[
  {
    "name": "data/big.bin",
    "type": "file",
    "size": 5000,
    "mtime": "2026-08-17 18:09:13"
  }
]
```

## Errors

`tarpeek` exits with a non-zero status and a message on stderr for:

- a path that does not exist
- a path that is not a valid tar archive
- an archive with no members (empty archive)
- an invalid `--min-size` value (negative)

## Running the tests

```bash
pip install -e ".[test]"
pytest
```
