"""Stdlib unittest suite for gitwho.py.

Drives the real gitwho.py CLI as a child process against real git fixture
repositories built by scripts/make_fixture_repo.sh. No git call in this
suite is mocked, stubbed or simulated (QUAL-01) -- every assertion here is
produced by the real `git` binary running against a real repository on
disk. Run from the repository root:

    python3 -m unittest discover -s tests -v

Do not pass -t . to `unittest discover`: without tests/__init__.py that
raises ImportError: Start directory is not importable (P2-05). This file
resolves every path from __file__ instead of the current directory, so it
runs correctly from anywhere.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GITWHO = REPO_ROOT / "gitwho.py"
FIXTURE_SCRIPT = REPO_ROOT / "scripts" / "make_fixture_repo.sh"

sys.path.insert(0, str(REPO_ROOT))
import gitwho  # noqa: E402  (import after sys.path manipulation is required)

FIXTURE_DIR = None
REPO = None
EMPTY_REPO = None
NOT_REPO = None

HEADER_RE = re.compile(r"^AUTHOR +COMMITS +ADDED +DELETED +FIRST +LAST$")
JSON_KEYS = ["name", "email", "commits", "added", "deleted", "first_commit", "last_commit"]


def setUpModule():
    global FIXTURE_DIR, REPO, EMPTY_REPO, NOT_REPO
    FIXTURE_DIR = Path(tempfile.mkdtemp(prefix="gitwho-tests-"))

    REPO = FIXTURE_DIR / "repo"
    subprocess.run(
        ["bash", str(FIXTURE_SCRIPT), str(REPO)],
        check=True,
        capture_output=True,
    )

    EMPTY_REPO = FIXTURE_DIR / "empty"
    subprocess.run(
        ["git", "init", "-q", "-b", "main", str(EMPTY_REPO)],
        check=True,
        capture_output=True,
    )

    NOT_REPO = FIXTURE_DIR / "not-a-repo"
    NOT_REPO.mkdir()
    (NOT_REPO / "file.txt").write_text("just an ordinary file\n")


def tearDownModule():
    if FIXTURE_DIR is not None:
        shutil.rmtree(FIXTURE_DIR, ignore_errors=True)


def run_cli(*args):
    """Run gitwho.py as a real child process. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(GITWHO), *args],
        capture_output=True,
    )
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    return result.returncode, stdout, stderr


def git_count(repo, *extra):
    """The oracle: how many commits does git itself count for this window."""
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-list", "--count", *extra, "HEAD"],
        check=True,
        capture_output=True,
    )
    return int(result.stdout.decode("utf-8").strip())


def data_rows(stdout):
    """Table data rows: everything after the header and separator lines."""
    lines = stdout.splitlines()
    return [line for line in lines[2:] if line.strip()]


def commits_column(row):
    """The COMMITS field, read from the right because author names have spaces."""
    return row.split()[-5]


class TestTableOutput(unittest.TestCase):
    def test_header_row_and_three_data_rows(self):
        code, stdout, stderr = run_cli(str(REPO))
        self.assertEqual(code, 0, stderr)
        lines = stdout.splitlines()
        self.assertRegex(lines[0], HEADER_RE)
        self.assertEqual(len(data_rows(stdout)), 3)

    def test_ann_adams_row_exact_figures(self):
        code, stdout, stderr = run_cli(str(REPO))
        self.assertEqual(code, 0, stderr)
        rows = data_rows(stdout)
        ann = next(r for r in rows if r.startswith("Ann Adams"))
        self.assertRegex(ann, r"^Ann Adams +3 +10 +5 +2024-01-01 +2024-01-04$")

    def test_binary_and_merge_do_not_inflate_line_counts(self):
        # Bob Brown's row is the combined proof that the binary file
        # contributed 0 lines (DATA-02) and the merge commit contributed
        # 1 commit and 0 lines (DATA-04).
        code, stdout, stderr = run_cli(str(REPO))
        self.assertEqual(code, 0, stderr)
        rows = data_rows(stdout)
        bob = next(r for r in rows if r.startswith("Bob Brown"))
        self.assertRegex(bob, r"^Bob Brown +3 +1 +0 +2024-01-03 +2024-01-06$")

    def test_non_utf8_author_row_present_and_exit_zero(self):
        code, stdout, stderr = run_cli(str(REPO))
        self.assertEqual(code, 0, stderr)
        rows = data_rows(stdout)
        bad = next((r for r in rows if re.search(r" Bad +\d", r)), None)
        self.assertIsNotNone(bad, rows)
        self.assertRegex(bad, r" Bad +1 +0 +0 +2024-01-07 +2024-01-07$")

    def test_commit_total_agrees_with_git_rev_list(self):
        code, stdout, stderr = run_cli(str(REPO))
        self.assertEqual(code, 0, stderr)
        rows = data_rows(stdout)
        total = sum(int(commits_column(r)) for r in rows)
        self.assertEqual(total, git_count(REPO))

    def test_rows_sorted_by_commits_descending(self):
        code, stdout, stderr = run_cli(str(REPO))
        self.assertEqual(code, 0, stderr)
        rows = data_rows(stdout)
        counts = [int(commits_column(r)) for r in rows]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_sorted_stats_pure_function_matches_cli_order(self):
        # Direct pure-function assertion against the imported module: the
        # in-process sorted_stats/aggregate pipeline must produce the same
        # author order as the CLI's rendered table.
        raw = gitwho.fetch_log(str(REPO))
        stats = gitwho.aggregate(gitwho.parse_log(raw))
        names_from_module = [s.name for s in gitwho.sorted_stats(stats)]

        code, stdout, stderr = run_cli(str(REPO))
        self.assertEqual(code, 0, stderr)
        names_from_cli = [row.split()[0] + " " + row.split()[1] for row in data_rows(stdout)]

        self.assertEqual(names_from_module, names_from_cli)


class TestSinceFilter(unittest.TestCase):
    SINCE = "2024-01-04T00:00:00+0000"
    FUTURE = "2099-01-01T00:00:00+0000"

    def test_since_window_restricts_to_four_commits(self):
        code, stdout, stderr = run_cli(f"--since={self.SINCE}", str(REPO))
        self.assertEqual(code, 0, stderr)
        rows = data_rows(stdout)
        self.assertEqual(len(rows), 3)
        total = sum(int(commits_column(r)) for r in rows)
        self.assertEqual(total, 4)

    def test_since_window_row_figures_exact(self):
        code, stdout, stderr = run_cli(f"--since={self.SINCE}", str(REPO))
        self.assertEqual(code, 0, stderr)
        rows = data_rows(stdout)
        bob = next(r for r in rows if r.startswith("Bob Brown"))
        self.assertRegex(bob, r"^Bob Brown +2 +1 +0 ")
        ann = next(r for r in rows if r.startswith("Ann Adams"))
        self.assertRegex(ann, r"^Ann Adams +1 +5 +5 +2024-01-04 +2024-01-04$")
        bad = next(r for r in rows if re.search(r" Bad +\d", r))
        self.assertRegex(bad, r" Bad +1 +0 +0 +2024-01-07 +2024-01-07$")

    def test_since_future_date_yields_empty_table_and_exit_zero(self):
        code, stdout, stderr = run_cli(f"--since={self.FUTURE}", str(REPO))
        self.assertEqual(code, 0, stderr)
        self.assertEqual(data_rows(stdout), [])
        self.assertRegex(stdout.splitlines()[0], HEADER_RE)

    def test_since_agrees_with_git_rev_list_count(self):
        for since in (self.SINCE, "2024-01-06T00:00:00+0000"):
            with self.subTest(since=since):
                code, stdout, stderr = run_cli(f"--since={since}", str(REPO))
                self.assertEqual(code, 0, stderr)
                rows = data_rows(stdout)
                total = sum(int(commits_column(r)) for r in rows)
                self.assertEqual(total, git_count(REPO, f"--since={since}"))


class TestJsonOutput(unittest.TestCase):
    def test_json_parses_and_is_a_list_of_objects(self):
        code, stdout, stderr = run_cli("--json", str(REPO))
        self.assertEqual(code, 0, stderr)
        data = json.loads(stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertTrue(all(isinstance(o, dict) for o in data))

    def test_json_key_order_and_types(self):
        code, stdout, stderr = run_cli("--json", str(REPO))
        self.assertEqual(code, 0, stderr)
        data = json.loads(stdout)
        for obj in data:
            self.assertEqual(list(obj.keys()), JSON_KEYS)
            self.assertIsInstance(obj["commits"], int)
            self.assertIsInstance(obj["added"], int)
            self.assertIsInstance(obj["deleted"], int)
            self.assertIsInstance(obj["first_commit"], str)
            self.assertIsInstance(obj["last_commit"], str)
            self.assertRegex(obj["first_commit"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertRegex(obj["last_commit"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(obj["email"])

    def test_json_matches_table_row_for_row(self):
        # Anti-drift guarantee (P2-08): the table and the JSON must agree
        # pairwise on order, name, commits, added, deleted and both dates.
        tcode, tstdout, tstderr = run_cli(str(REPO))
        jcode, jstdout, jstderr = run_cli("--json", str(REPO))
        self.assertEqual(tcode, 0, tstderr)
        self.assertEqual(jcode, 0, jstderr)
        rows = data_rows(tstdout)
        objs = json.loads(jstdout)
        self.assertEqual(len(rows), len(objs))
        for row, obj in zip(rows, objs):
            fields = row.split()
            name = " ".join(fields[:-5])
            commits, added, deleted, first, last = fields[-5:]
            self.assertEqual(name, obj["name"])
            self.assertEqual(int(commits), obj["commits"])
            self.assertEqual(int(added), obj["added"])
            self.assertEqual(int(deleted), obj["deleted"])
            self.assertEqual(first, obj["first_commit"])
            self.assertEqual(last, obj["last_commit"])

    def test_json_respects_since_flag(self):
        since = "2024-01-04T00:00:00+0000"
        code, stdout, stderr = run_cli("--json", f"--since={since}", str(REPO))
        self.assertEqual(code, 0, stderr)
        data = json.loads(stdout)
        self.assertEqual(len(data), 3)
        self.assertEqual(sum(o["commits"] for o in data), 4)
        self.assertEqual(data[0]["name"], "Bob Brown")

    def test_json_empty_window_is_empty_array(self):
        code, stdout, stderr = run_cli("--json", "--since=2099-01-01T00:00:00+0000", str(REPO))
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stdout.rstrip("\n"), "[]")
        self.assertEqual(json.loads(stdout), [])


class TestErrorContract(unittest.TestCase):
    def test_not_a_repo_exits_two_with_clear_message(self):
        code, stdout, stderr = run_cli(str(NOT_REPO))
        self.assertEqual(code, 2)
        self.assertIn("is not a git repository", stderr)

    def test_nonexistent_path_exits_two(self):
        code, stdout, stderr = run_cli(str(NOT_REPO / "does-not-exist"))
        self.assertEqual(code, 2)

    def test_empty_repo_exits_one_with_clear_message(self):
        code, stdout, stderr = run_cli(str(EMPTY_REPO))
        self.assertEqual(code, 1)
        self.assertIn("has no commits", stderr)

    def test_error_paths_print_nothing_to_stdout(self):
        for path in (NOT_REPO, NOT_REPO / "does-not-exist", EMPTY_REPO):
            with self.subTest(path=path):
                code, stdout, stderr = run_cli(str(path))
                self.assertNotEqual(code, 0)
                self.assertEqual(stdout, "")

    def test_error_paths_do_not_leak_git_diagnostics(self):
        for path in (NOT_REPO, NOT_REPO / "does-not-exist", EMPTY_REPO):
            with self.subTest(path=path):
                code, stdout, stderr = run_cli(str(path))
                self.assertNotEqual(code, 0)
                self.assertNotIn("fatal:", stderr)


if __name__ == "__main__":
    unittest.main()
