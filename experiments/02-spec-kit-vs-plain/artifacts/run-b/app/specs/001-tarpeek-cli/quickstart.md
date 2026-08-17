# Quickstart: Validating `tarpeek`

This guide proves the feature works end-to-end after implementation. It does not contain
implementation code — see [data-model.md](./data-model.md) and
[contracts/cli-interface.md](./contracts/cli-interface.md) for the field/format details being
validated here.

## Prerequisites

- Python 3.9+
- A checkout of this repository on the `001-tarpeek-cli` branch

## 1. Install

From the repository root:

```bash
pip install .
```

This installs the `tarpeek` console script onto PATH (FR-012, SC-006). Verify it resolves from a
directory outside the checkout:

```bash
cd /tmp
tarpeek --help
```

Expected: usage help is printed; the command is found regardless of current working directory.

## 2. Build a sample archive to inspect

```bash
mkdir -p /tmp/tarpeek-demo/subdir
echo "hello" > /tmp/tarpeek-demo/small.txt
head -c 5000 /dev/urandom > /tmp/tarpeek-demo/big.bin
ln -s small.txt /tmp/tarpeek-demo/link-to-small
tar -C /tmp/tarpeek-demo -cf /tmp/demo.tar small.txt big.bin subdir link-to-small
```

## 3. Validate User Story 1 — basic listing

```bash
tarpeek /tmp/demo.tar
```

Expected: a table with one row per member (`small.txt`, `big.bin`, `subdir`, `link-to-small`),
correct `file`/`dir`/`symlink` types, correct byte sizes, ISO 8601 UTC last-modified timestamps,
sorted by size descending (ties broken alphabetically). Confirm no new files appear anywhere
outside `/tmp/tarpeek-demo` and `/tmp/demo.tar` (FR-007) — e.g. diff a `find /tmp` snapshot taken
before and after the command.

## 4. Validate User Story 2 — `--min-size` filtering

```bash
tarpeek /tmp/demo.tar --min-size 4000
```

Expected: only `big.bin` (>= 4000 bytes) is listed.

```bash
tarpeek /tmp/demo.tar --min-size 999999999
```

Expected: empty result set, exit code `0` (success — see contracts/cli-interface.md).

## 5. Validate User Story 3 — `--json` output

```bash
tarpeek /tmp/demo.tar --json | python3 -m json.tool
```

Expected: valid JSON parses without error; top-level array of objects with keys `name`, `type`,
`size`, `last_modified`; same sort order as the table.

```bash
tarpeek /tmp/demo.tar --min-size 4000 --json
```

Expected: JSON array containing only `big.bin`.

## 6. Validate error paths

```bash
tarpeek /tmp/does-not-exist.tar; echo "exit=$?"
echo "not a tar file" > /tmp/not-a-tar.txt
tarpeek /tmp/not-a-tar.txt; echo "exit=$?"
tar -cf /tmp/empty.tar -T /dev/null; tarpeek /tmp/empty.tar; echo "exit=$?"
tarpeek /tmp/demo.tar --min-size=-5; echo "exit=$?"
```

Expected for each: a clear, distinct error message on stderr and the same non-zero exit code
(FR-008–FR-011a) — verify by comparing the `exit=` values across all four (equal) and the message
text (all different).

## 7. Run the automated test suite

```bash
pytest
```

Expected: all tests pass, covering the scenarios above (FR-013) plus the filesystem-write
guarantee (FR-007).
