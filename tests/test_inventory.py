import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "inventory", Path(__file__).resolve().parents[1] / "scripts/inventory.py"
)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_sorted_unique_lines(self):
        self.assertEqual(inventory.lines("z\na\nz"), "a\nz\n")
        self.assertEqual(inventory.lines(""), "")

    def test_no_foreign_packages_is_valid(self):
        result = subprocess.CompletedProcess(["pacman"], 1, "", "")
        with patch.object(inventory.subprocess, "run", return_value=result):
            self.assertEqual(inventory.run("pacman", "-Qqem", allow_empty=True), "")

    def test_package_errors_are_not_swallowed(self):
        result = subprocess.CompletedProcess(["pacman"], 1, "", "database unavailable")
        with patch.object(inventory.subprocess, "run", return_value=result):
            with self.assertRaises(subprocess.CalledProcessError):
                inventory.run("pacman", "-Qqem", allow_empty=True)

    def test_repeated_capture_does_not_rewrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(inventory, "ROOT", root), \
                 patch.object(inventory.socket, "gethostname", return_value="test-host"), \
                 patch.object(inventory, "collect", return_value={"packages.txt": "a\n"}):
                inventory.main()
                path = root / "inventory/test-host/packages.txt"
                modified = path.stat().st_mtime_ns
                inventory.main()
                self.assertEqual(path.stat().st_mtime_ns, modified)
                self.assertEqual(path.read_text(), "a\n")

    def test_query_failure_preserves_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "inventory/test-host/packages.txt"
            path.parent.mkdir(parents=True)
            path.write_text("old\n")
            with patch.object(inventory, "ROOT", root), \
                 patch.object(inventory.socket, "gethostname", return_value="test-host"), \
                 patch.object(inventory, "collect", side_effect=RuntimeError("query failed")):
                with self.assertRaises(RuntimeError):
                    inventory.main()
            self.assertEqual(path.read_text(), "old\n")


if __name__ == "__main__":
    unittest.main()
