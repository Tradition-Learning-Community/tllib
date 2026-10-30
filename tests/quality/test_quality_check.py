"""Changed-source CI scope probes (synthetic Git history, no network)."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools import quality_check as quality  # noqa: E402


class QualityScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "test")
        (self.repo / "docs").mkdir()
        (self.repo / "docs/page.md").write_text("original\n", encoding="utf-8")
        (self.repo / "sample.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "baseline")

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            timeout=30,
        )

    def test_docs_only_has_no_source_checks(self) -> None:
        (self.repo / "docs/page.md").write_text("updated\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "docs only")
        self.assertEqual(quality.modified(self.repo, "HEAD^"), [])

    def test_changed_cpp_line_range_is_detected(self) -> None:
        (self.repo / "sample.cpp").write_text("int main() { return 1; }\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "native changed")
        self.assertEqual(quality.modified(self.repo, "HEAD^"), [("M", "sample.cpp")])
        self.assertEqual(quality.changed_lines(self.repo, "HEAD^", "sample.cpp"), ["--lines=1:1"])

    def test_hunk_parser(self) -> None:
        self.assertEqual(quality.HUNK.match("@@ -3,2 +8,5 @@").groups(), ("8", "5"))


if __name__ == "__main__":
    unittest.main()
