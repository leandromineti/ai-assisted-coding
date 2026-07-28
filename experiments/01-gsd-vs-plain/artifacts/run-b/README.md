# gitwho

A Python CLI that summarizes contributor activity for a git repository.

One command against any git repo produces a correct, readable per-author activity
summary. Correctness means agreeing with what git itself reports: gitwho's numbers are
cross-checked against `git rev-list --count` and `git log` throughout its test suite,
and it never invents a figure git wouldn't also produce.

## Requirements

- Python 3.11 or newer
- `git` on `PATH`

gitwho has no third-party dependencies and nothing to install — it is one file,
`gitwho.py`. The git flags it relies on (`--numstat`, `--no-renames`, `--format`,
`rev-parse`) have been stable in git for well over a decade, so any git 2.x is fine.

## Usage

```
python3 gitwho.py [path] [--since DATE] [--json]
```

`path` defaults to the current directory.

Run against a repository:

```
$ python3 gitwho.py /tmp/gitwho-demo
AUTHOR     COMMITS  ADDED  DELETED  FIRST       LAST
---------  -------  -----  -------  ----------  ----------
Ann Adams        3     10        5  2024-01-01  2024-01-04
Bob Brown        3      1        0  2024-01-03  2024-01-06
Andr� Bad        1      0        0  2024-01-07  2024-01-07
```

Combine both flags — narrow the window and get JSON back:

```
$ python3 gitwho.py /tmp/gitwho-demo --since=2024-01-04T00:00:00+0000 --json
[
  {
    "name": "Bob Brown",
    "email": "bob@example.com",
    "commits": 2,
    "added": 1,
    "deleted": 0,
    "first_commit": "2024-01-05",
    "last_commit": "2024-01-06"
  },
  {
    "name": "Andr\ufffd Bad",
    "email": "bad@example.com",
    "commits": 1,
    "added": 0,
    "deleted": 0,
    "first_commit": "2024-01-07",
    "last_commit": "2024-01-07"
  },
  {
    "name": "Ann Adams",
    "email": "ann@example.com",
    "commits": 1,
    "added": 5,
    "deleted": 5,
    "first_commit": "2024-01-04",
    "last_commit": "2024-01-04"
  }
]
```

## Flags

| Flag | Argument | Description |
|------|----------|-------------|
| `path` | (positional, optional) | Path to a git repository. Defaults to the current directory. |
| `--since` | `DATE` | Restrict the summary to commits since `DATE`, handed to git verbatim. |
| `--json` | (none) | Emit machine-readable JSON instead of the table. |
| `-h`, `--help` | (none) | Show the help message and exit. |

## Dates and --since

`--since` hands its value to git verbatim, so anything git accepts works: a plain date
like `2024-01-01`, a full ISO timestamp with an offset like
`2024-01-04T00:00:00+0000`, or a relative expression like `"3 weeks ago"`.

git resolves a bare date (no offset) in the machine's local timezone, so a bare
`--since=2024-01-04` can select a different set of commits on two machines in different
timezones. Pass an explicit `+0000` offset when you need the same answer everywhere.

`--since` filters on each commit's **committer date**, while the FIRST and LAST columns
display the **author date**. For most repositories these are the same instant, but for
rebased or cherry-picked history they diverge.

Most importantly: git does not reject a date it cannot parse. An unparseable value
resolves to the current time, which yields an empty window and exit code 0 — not an
error. A typo in `--since` can therefore silently produce an empty result. This is the
one way gitwho can mislead you, and there is no way to detect it from the tool's output
alone.

## JSON output

`--json` prints a top-level array, one object per author, ordered exactly like the
table (commit count descending, name ascending as a tiebreak). Each object has these
seven keys, in this order:

| Key | Type | Notes |
|-----|------|-------|
| `name` | string | Author name as git reports it (`%an`) |
| `email` | string | Author email; the table does not show this column |
| `commits` | integer | Commit count for this author |
| `added` | integer | Total lines added |
| `deleted` | integer | Total lines deleted |
| `first_commit` | string or `null` | `YYYY-MM-DD`, UTC |
| `last_commit` | string or `null` | `YYYY-MM-DD`, UTC |

```json
[
  {
    "name": "Ann Adams",
    "email": "ann@example.com",
    "commits": 3,
    "added": 10,
    "deleted": 5,
    "first_commit": "2024-01-01",
    "last_commit": "2024-01-04"
  },
  {
    "name": "Bob Brown",
    "email": "bob@example.com",
    "commits": 3,
    "added": 1,
    "deleted": 0,
    "first_commit": "2024-01-03",
    "last_commit": "2024-01-06"
  },
  {
    "name": "Andr\ufffd Bad",
    "email": "bad@example.com",
    "commits": 1,
    "added": 0,
    "deleted": 0,
    "first_commit": "2024-01-07",
    "last_commit": "2024-01-07"
  }
]
```

Non-ASCII characters in author names are escaped as `\uXXXX`, which every JSON parser
decodes correctly. `email` appears in the JSON output although the table shows names
only — that is the documented difference between the two output modes.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success — including a valid repository whose `--since` window selects nothing |
| 1 | The repository has no commits (or an unexpected git failure occurred) |
| 2 | The path is not a git repository — including a path that does not exist |

## How commits are counted

Merge commits count as one commit for their author and contribute no line stats.

Binary files report no line numbers in git's numstat output, so they contribute zero
added and zero deleted lines while still counting toward the commit. Renames are
counted as a deletion plus an addition, because gitwho always passes `--no-renames` —
this pins the output shape no matter how the reader's own git is configured. An author
name carrying bytes that are not valid UTF-8 is decoded with replacement rather than
crashing the run, so such a name displays with a replacement character (as in the
`Andr� Bad` example above).

## Author identity

Authors are grouped by the `(name, email)` pair, so one person committing under two
email addresses appears as two separate rows.

gitwho does not merge identities and does not consult `.mailmap`: git's `%an`
placeholder, which gitwho uses, returns the raw author name and is not rewritten by
`.mailmap` — only the capitalized `%aN` placeholder applies that mapping. This is
deliberate: correctness for this tool means agreeing with what git itself reports.

## Running the tests

```
python3 -m unittest discover -s tests -v
```

Run this from the repository root. The suite builds real git repositories with
`scripts/make_fixture_repo.sh` and runs the real `gitwho.py` CLI as a child process
against them — nothing about git is simulated. This is why the tests need `git` on
`PATH`, and why they prove the behaviours documented above rather than merely restating
them.
