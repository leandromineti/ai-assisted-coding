# logpeek

A small CLI that summarizes structured log files.

For each file given, it prints:

- total lines in the file
- a count of entries per log level
- the time span covered (timestamp of the first and last event)
- the five most frequent logger names

## Install

From the project root:

```bash
pip install .
```

(or `pip install -e .` for an editable/development install). This registers a
`logpeek` console script on your `PATH`, so it can be run from any directory:

```bash
cd /tmp
logpeek /path/to/some.log
```

## Usage

```bash
logpeek FILE [FILE ...] [--level NAME] [--json]
```

- Multiple files may be given; each is summarized independently.
- `--level NAME` restricts the summary to entries at that log level
  (case-insensitive, e.g. `--level error`). Level counts, time span, and top
  loggers are then computed only over matching entries.
- `--json` prints a JSON array with one object per input file instead of the
  default text report, for scripting/machine consumption.

### Example

```
$ logpeek samples/boot.log
==> samples/boot.log <==
Total lines:     6
Parsed entries:  6
Time span:       2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
Level counts:
  INFO       4
  DEBUG      1
  WARNING    1
Top loggers:
  boot.init            3
  boot.svc             3
```

```
$ logpeek --json --level ERROR samples/boot.log
[
  {
    "file": "samples/boot.log",
    "error": null,
    "total_lines": 6,
    "parsed_lines": 6,
    "unparsed_lines": 0,
    "level_filter": "ERROR",
    "matched_lines": 0,
    "level_counts": {},
    "time_span": { "first": null, "last": null },
    "top_loggers": []
  }
]
```

## Log line format

Each line is expected to look like:

```
<timestamp> <LEVEL> <logger.name>: <message>
```

`<timestamp>` may be either an ISO-8601 timestamp with a UTC offset
(`2026-06-01T00:00:00+00:00`) or an integer Unix epoch in seconds
(`1767233000`). Both forms may appear in the same file.

## Error handling

logpeek never opens an input file for writing, so it can never modify what
you point it at.

Lines that don't match the expected format (corrupted fragments, log-rotation
markers, truncated timestamps, etc.) are skipped and counted as "unparsed" —
they don't stop the rest of the file from being summarized, and a single
non-UTF-8 byte inside a message is tolerated (replaced) rather than aborting
the whole read.

Whole-file problems are reported as clear errors with a non-zero exit code,
rather than a stack trace:

- a missing path
- an empty file
- a file with no line that resembles a log entry at all (e.g. a binary file
  or arbitrary text)

When multiple files are given, one file's error doesn't stop the others from
being summarized — the file-level error is reported (to stderr in text mode,
or as an `"error"` field per entry in `--json` mode) and the process exits
non-zero if any file failed.

## Development

```bash
pip install -e ".[test]"
pytest
```

Tests cover the parser, the aggregation logic, and the CLI end-to-end,
including the bundled `samples/` files (a normal small log, a large log with
mixed timestamp formats and several kinds of corruption, and an empty file)
plus fixtures for non-log input.
