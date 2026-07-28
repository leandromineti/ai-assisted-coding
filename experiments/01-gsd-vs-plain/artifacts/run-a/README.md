# gitwho

Summarize contributor activity for a git repository.

```sh
python3 gitwho.py [REPO] [--since DATE] [--json]
```

Prints a per-author table — commits, lines added/deleted, first and last commit date —
sorted by commit count. `--since` accepts anything `git log --since` does. `--json`
emits the same data as JSON. Exits 2 if `REPO` is not a git repository, 1 if it has no
commits.

## Tests

```sh
python3 -m unittest test_gitwho
```

Tests build real throwaway git repos rather than mocking git.
