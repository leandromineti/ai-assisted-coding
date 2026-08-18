# logpeek

A small CLI that summarizes structured log files: total lines, a count per
log level, the time span covered, and the five most frequent logger names.

## Install

From the project directory:

```sh
pip install .
```

(or `pip install -e .` for an editable/development install). Either way this
puts a `logpeek` executable on your `PATH`, runnable from any directory.

## Usage

```sh
logpeek FILE [FILE ...]
logpeek --level ERROR access.log
logpeek --json *.log
```

Options:

- `--level NAME` — only include log entries at the given level (case
  insensitive, e.g. `--level warning`). Restricts the level counts, time
  span, and top-logger ranking to matching entries; the raw/parsed line
  counts for the file are unaffected, so you can still see how much of the
  file matched.
- `--json` — print a JSON array (one object per input file) instead of
  plain text, for machine consumption.

Multiple files are summarized independently, one block each. If some files
fail (see below) and others succeed, the successful ones still print;
the process exits non-zero if *any* file failed.

### Example

```
$ logpeek samples/boot.log
==> samples/boot.log <==
Total lines: 6 (6 parsed, 0 unparsed)
Time span: 2026-05-31T23:58:00+00:00 -> 2026-05-31T23:58:07+00:00
Level counts:
  DEBUG: 1
  INFO: 4
  WARNING: 1
Top loggers:
  boot.init: 3
  boot.svc: 3
```

## Expected log format

Each line is expected to look like:

```
<timestamp> <LEVEL> <logger.name>: <message>
```

Timestamps may be either ISO 8601 (with a UTC or local offset, e.g.
`2026-06-01T00:00:00+00:00`) or Unix epoch seconds (e.g. `1767233000`) — a
single file may mix both. Lines that don't match this shape at all, or whose
timestamp can't be parsed, are counted as "unparsed" and skipped rather than
aborting the whole run — real-world logs often have a handful of corrupted
or truncated lines (partial writes, log rotation markers, stray non-log
output) mixed in with otherwise-valid entries.

## Error handling

- **Empty file**: reported as a clear per-file error (`file is empty`);
  non-zero exit code.
- **Not a log file** (a file with content, but zero lines matching the
  expected format): reported as `no parsable log lines found (not a
  recognized log format)`; non-zero exit code.
- **Missing / unreadable file**: reported with a clear message (`no such
  file`, `permission denied`, `is a directory`); non-zero exit code.
- In `--json` mode, per-file errors are reported inline as
  `{"path": ..., "error": ...}` instead of going to stderr, so the JSON
  output always parses even when some files fail.

`logpeek` only ever opens input files for reading — it never writes to,
renames, or truncates them.

## Development

```sh
pip install -e .
pip install pytest
pytest
```

Tests live in `tests/` and include unit tests for the parser plus CLI tests
run against the fixtures in `samples/` (which intentionally include a
malformed-but-mostly-valid log, a clean log, and an empty file).
