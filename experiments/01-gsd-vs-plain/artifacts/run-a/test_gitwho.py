"""Tests for gitwho. They build real throwaway git repos — no mocked git."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import gitwho


def make_repo(commits: list[tuple[str, str, dict[str, str]]]) -> str:
    """commits: list of (author, date, {filename: content})."""
    repo = tempfile.mkdtemp()
    subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
    for author, date, files in commits:
        for name, content in files.items():
            Path(repo, name).write_text(content)
        subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
        env_date = f"{date}T12:00:00"
        subprocess.run(
            ["git", "-C", repo, "-c", f"user.name={author}",
             "-c", "user.email=t@t", "commit", "-q", "-m", "c",
             f"--date={env_date}"],
            check=True,
            env={"GIT_COMMITTER_DATE": env_date, "PATH": "/usr/bin:/bin"},
        )
    return repo


class GitwhoTests(unittest.TestCase):
    def test_counts_commits_and_lines_per_author(self):
        repo = make_repo([
            ("alice", "2026-01-01", {"a.txt": "one\ntwo\n"}),
            ("bob", "2026-01-02", {"b.txt": "x\n"}),
            ("alice", "2026-01-03", {"a.txt": "one\n"}),  # deletes a line
        ])
        authors = gitwho.collect(repo, None)
        self.assertEqual(authors["alice"].commits, 2)
        self.assertEqual(authors["alice"].added, 2)
        self.assertEqual(authors["alice"].deleted, 1)
        self.assertEqual(authors["bob"].commits, 1)
        self.assertEqual(authors["alice"].first, "2026-01-01")
        self.assertEqual(authors["alice"].last, "2026-01-03")

    def test_since_filters_old_commits(self):
        repo = make_repo([
            ("alice", "2026-01-01", {"a.txt": "one\n"}),
            ("bob", "2026-06-01", {"b.txt": "x\n"}),
        ])
        authors = gitwho.collect(repo, "2026-03-01")
        self.assertNotIn("alice", authors)
        self.assertIn("bob", authors)

    def test_json_output_is_valid_and_sorted(self):
        repo = make_repo([
            ("alice", "2026-01-01", {"a.txt": "one\n"}),
            ("alice", "2026-01-02", {"b.txt": "x\n"}),
            ("bob", "2026-01-03", {"c.txt": "y\n"}),
        ])
        import contextlib, io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = gitwho.main([repo, "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(list(payload)[0], "alice")  # most commits first
        self.assertEqual(payload["bob"]["commits"], 1)

    def test_not_a_repo_exits_2(self):
        plain_dir = tempfile.mkdtemp()
        code = gitwho.main([plain_dir])
        self.assertEqual(code, 2)

    def test_empty_repo_exits_1(self):
        repo = tempfile.mkdtemp()
        subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
        code = gitwho.main([repo])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
