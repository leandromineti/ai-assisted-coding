# logpeek

A small CLI that summarizes structured log files. For each file given, it
reports:

- total lines
- a count of entries per log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- the time span covered (timestamp of the first and last event)
- the five most frequent logger names

## Expected log format

Each line is expected to look like:

```
TIMESTAMP LEVEL LOGGER.NAME: message text
```

- `TIMESTAMP` is either an ISO-8601 timestamp (e.g. `2026-06-01T00:00:00+00:00`)
  or a Unix epoch in seconds (e.g. `1767233000`). Bare integer timestamps are
  only trusted within a plausible calendar range (years 2000-2099) — this
  guards against sentinel/garbage values (e.g. `0` or `4294967295`) silently
  blowing out the reported time span.
- `LEVEL` is one of the five standard levels above.
- Lines that don't match this shape (truncated lines, embedded blobs,
  rotation banners, etc.) are skipped and counted separately as
  "unparseable" rather than crashing the tool.

## Install

From the project directory:

```bash
pip install .
```

or, for an editable install while developing:

```bash
pip install -e ".[test]"
```

Either way this installs a `logpeek` console script on your `PATH`, runnable
from any directory.

## Usage

```bash
logpeek path/to/file.log [more/files.log ...]
logpeek --level ERROR path/to/file.log     # only include ERROR entries
logpeek --json path/to/file.log            # machine-readable output
```

Example:

```
$ logpeek samples/boot.log
== samples/boot.log ==
Total lines: 6
Parsed entries: 6 (unparseable: 0)
Level counts:
  DEBUG: 1
  INFO: 4
  WARNING: 1
  ERROR: 0
  CRITICAL: 0
Time span: 2026-05-31T23:58:00+00:00 -> 2026-05-31T23:58:07+00:00
Top 5 loggers:
  boot.init: 3
  boot.svc: 3
```

Multiple files are summarized one after another (or as a JSON array of
per-file objects with `--json`). Errors on individual files (missing,
empty, or not a recognizable log file) are printed to stderr and don't stop
the other files from being processed; the process exits non-zero if any
file failed.

`logpeek` only ever opens input files for reading — it never writes to or
modifies them.

## Development

```bash
pip install -e ".[test]"
python3 -m pytest
```

Tests cover the parser, the summary logic, the CLI's error handling, and an
end-to-end run against every file in `../samples/` (a large log with
embedded garbage/legacy-timestamp lines, a small clean log, and an empty
file).
