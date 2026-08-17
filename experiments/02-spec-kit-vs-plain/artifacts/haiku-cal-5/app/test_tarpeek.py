"""Tests for tarpeek CLI."""

import json
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


class TestTarpeek(unittest.TestCase):
    """Test tarpeek functionality."""

    def setUp(self):
        """Create temporary directory and test archives."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def run_tarpeek(self, *args):
        """Run tarpeek and return stdout, stderr, returncode."""
        result = subprocess.run(
            ["python", "-m", "tarpeek"] + list(args),
            capture_output=True,
            text=True,
        )
        return result.stdout, result.stderr, result.returncode

    def create_simple_archive(self):
        """Create a simple tar archive with test files."""
        archive_path = self.temp_path / "test.tar"

        with tarfile.open(archive_path, "w") as tar:
            # Create file1.txt
            import io
            content = b"Hello, world!"
            info = tarfile.TarInfo(name="file1.txt")
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

            # Create dir/
            dir_info = tarfile.TarInfo(name="dir/")
            dir_info.type = tarfile.DIRTYPE
            tar.addfile(dir_info)

            # Create dir/file2.txt
            content2 = b"Larger file content here" * 100
            info2 = tarfile.TarInfo(name="dir/file2.txt")
            info2.size = len(content2)
            tar.addfile(info2, io.BytesIO(content2))

            # Create symlink
            link_info = tarfile.TarInfo(name="link")
            link_info.type = tarfile.SYMTYPE
            link_info.linkname = "file1.txt"
            tar.addfile(link_info)

        return str(archive_path)

    def test_simple_archive(self):
        """Test reading a simple archive."""
        archive = self.create_simple_archive()
        stdout, stderr, code = self.run_tarpeek(archive)

        self.assertEqual(code, 0)
        self.assertIn("file1.txt", stdout)
        self.assertIn("dir", stdout)
        self.assertIn("file2.txt", stdout)
        self.assertIn("link", stdout)
        self.assertEqual(stderr, "")

    def test_member_types(self):
        """Test that member types are correctly identified."""
        archive = self.create_simple_archive()
        stdout, stderr, code = self.run_tarpeek(archive)

        self.assertEqual(code, 0)
        lines = stdout.split("\n")

        # Find lines with each member and check type
        for line in lines:
            if "file1.txt" in line:
                self.assertIn("file", line)
            elif "file2.txt" in line:
                self.assertIn("file", line)
            elif "dir" in line and "file" not in line:
                self.assertIn("dir", line)
            elif "link" in line:
                self.assertIn("symlink", line)

    def test_sorted_by_size_descending(self):
        """Test that output is sorted by size descending."""
        archive = self.create_simple_archive()
        stdout, stderr, code = self.run_tarpeek(archive)

        self.assertEqual(code, 0)

        # Extract size column and verify descending order
        lines = stdout.split("\n")[2:]  # Skip header and separator
        sizes = []
        for line in lines:
            if line.strip() and not line.startswith("-"):
                parts = line.split()
                # Size is in the 3rd column (index 2)
                if len(parts) >= 3:
                    try:
                        size = int(parts[2])
                        sizes.append(size)
                    except ValueError:
                        pass

        # Verify sizes are in descending order
        for i in range(len(sizes) - 1):
            self.assertGreaterEqual(sizes[i], sizes[i + 1])

    def test_min_size_filter(self):
        """Test --min-size filtering."""
        archive = self.create_simple_archive()
        stdout, stderr, code = self.run_tarpeek(archive, "--min-size", "500")

        self.assertEqual(code, 0)
        # Only file2.txt should be >= 500 bytes
        self.assertIn("file2.txt", stdout)
        self.assertNotIn("file1.txt", stdout)

    def test_json_output(self):
        """Test --json output format."""
        archive = self.create_simple_archive()
        stdout, stderr, code = self.run_tarpeek(archive, "--json")

        self.assertEqual(code, 0)

        # Parse JSON output
        data = json.loads(stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        # Check structure of first member
        member = data[0]
        self.assertIn("name", member)
        self.assertIn("type", member)
        self.assertIn("size", member)
        self.assertIn("mtime", member)

    def test_json_sorted_by_size(self):
        """Test JSON output is sorted by size descending."""
        archive = self.create_simple_archive()
        stdout, stderr, code = self.run_tarpeek(archive, "--json")

        self.assertEqual(code, 0)
        data = json.loads(stdout)

        # Verify sorted by size descending
        sizes = [m["size"] for m in data]
        self.assertEqual(sizes, sorted(sizes, reverse=True))

    def test_not_a_tar_archive(self):
        """Test handling of non-tar file."""
        non_tar = self.temp_path / "notatar.txt"
        non_tar.write_text("This is not a tar file")

        stdout, stderr, code = self.run_tarpeek(str(non_tar))

        self.assertNotEqual(code, 0)
        self.assertIn("Not a valid tar archive", stderr)

    def test_file_not_found(self):
        """Test handling of missing archive."""
        stdout, stderr, code = self.run_tarpeek("/nonexistent/archive.tar")

        self.assertNotEqual(code, 0)
        self.assertIn("not found", stderr.lower())

    def test_empty_archive(self):
        """Test handling of empty archive."""
        archive_path = self.temp_path / "empty.tar"

        with tarfile.open(archive_path, "w") as tar:
            pass  # Create empty archive

        stdout, stderr, code = self.run_tarpeek(str(archive_path))

        self.assertEqual(code, 0)
        self.assertIn("Empty archive", stdout)
        self.assertEqual(stderr, "")

    def test_min_size_with_json(self):
        """Test combining --min-size and --json."""
        archive = self.create_simple_archive()
        stdout, stderr, code = self.run_tarpeek(archive, "--min-size", "500", "--json")

        self.assertEqual(code, 0)
        data = json.loads(stdout)

        # All returned members should be >= 500 bytes
        for member in data:
            self.assertGreaterEqual(member["size"], 500)

    def test_large_archive(self):
        """Test with larger archive."""
        archive_path = self.temp_path / "large.tar"

        with tarfile.open(archive_path, "w") as tar:
            import io
            # Add many files
            for i in range(100):
                content = (b"x" * (i * 100))
                info = tarfile.TarInfo(name=f"file{i:03d}.txt")
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))

        stdout, stderr, code = self.run_tarpeek(str(archive_path))

        self.assertEqual(code, 0)
        for i in range(100):
            self.assertIn(f"file{i:03d}.txt", stdout)


if __name__ == "__main__":
    unittest.main()
