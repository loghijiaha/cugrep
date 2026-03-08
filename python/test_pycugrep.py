
import unittest
import subprocess
import os
import sys
import shutil
from importlib.resources import files as importlib_files

class TestPyCuGrep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Change to the package directory to install
        cls.original_cwd = os.getcwd()
        os.chdir(os.path.join("/content/cugrep", "python"))

        # Install pycugrep in editable mode
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("\nInstalled pycugrep in editable mode.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing pycugrep: {e.stdout}\n{e.stderr}", file=sys.stderr)
            sys.exit(1)

        # Create a temporary directory for test files
        cls.test_dir = "/tmp/pycugrep_test_data"
        os.makedirs(cls.test_dir, exist_ok=True)

        # Create test files
        cls.file1_path = os.path.join(cls.test_dir, "file1.txt")
        with open(cls.file1_path, "w") as f:
            f.write("apple\nbanana\norange\nApple\n")

        cls.file2_path = os.path.join(cls.test_dir, "file2.txt")
        with open(cls.file2_path, "w") as f:
            f.write("grape\nPineapple\npear\n")

        # Dynamically locate the cli.py script using the installed package
        try:
            cls.cugrep_cli = str(importlib_files('pycugrep').joinpath('cli.py'))
        except Exception as e:
            print(f"Error locating cli.py after install: {e}", file=sys.stderr)
            sys.exit(1)


    @classmethod
    def tearDownClass(cls):
        # Uninstall pycugrep
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "pycugrep"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("\nUninstalled pycugrep.")
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling pycugrep: {e.stdout}\n{e.stderr}", file=sys.stderr)

        # Clean up temporary test files
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

        # Revert to original working directory
        os.chdir(cls.original_cwd)

    def _run_cugrep(self, pattern, files, options=None):
        command = [sys.executable, self.cugrep_cli, pattern] + files
        if options:
            # Insert options before pattern
            command = [sys.executable, self.cugrep_cli] + options + [pattern] + files

        # Set LD_LIBRARY_PATH dynamically if it's not already set, or append
        env = os.environ.copy()
        try:
            kvikio_lib_path_candidate = str(importlib_files('libkvikio').joinpath('lib64'))
            if os.path.exists(kvikio_lib_path_candidate):
                current_ld_library_path = env.get('LD_LIBRARY_PATH', '')
                if kvikio_lib_path_candidate not in current_ld_library_path:
                    env['LD_LIBRARY_PATH'] = f"{kvikio_lib_path_candidate}:{current_ld_library_path}"
        except Exception:
            pass # libkvikio might not be installed, proceed without setting LD_LIBRARY_PATH

        result = subprocess.run(command, capture_output=True, text=True, check=False, env=env)
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    def test_basic_grep(self):
        stdout, stderr, rc = self._run_cugrep("banana", [self.file1_path])
        self.assertEqual(rc, 0)
        self.assertIn("banana", stdout)
        self.assertNotIn("apple", stdout)
        self.assertIn("2:banana", stdout) # Corrected line number test (was 1:banana)

    def test_ignore_case(self):
        stdout, stderr, rc = self._run_cugrep("apple", [self.file1_path], options=["-i"])
        self.assertEqual(rc, 0)
        self.assertIn("apple", stdout)
        self.assertIn("Apple", stdout)
        self.assertIn("1:apple", stdout) # Corrected line number test (was 0:apple)
        self.assertIn("4:Apple", stdout) # Corrected line number test (was 3:Apple)

    def test_count_only(self):
        stdout, stderr, rc = self._run_cugrep("apple", [self.file1_path], options=["-i", "-c"])
        self.assertEqual(rc, 0)
        self.assertIn(f"{self.file1_path}: 2", stdout)

    def test_invert_match(self):
        stdout, stderr, rc = self._run_cugrep("orange", [self.file1_path], options=["-v"])
        self.assertEqual(rc, 0)
        self.assertIn("apple", stdout)
        self.assertIn("banana", stdout)
        self.assertIn("Apple", stdout)
        self.assertNotIn("orange", stdout)

    def test_multiple_files(self):
        stdout, stderr, rc = self._run_cugrep("apple", [self.file1_path, self.file2_path], options=["-i"])
        self.assertEqual(rc, 0)
        self.assertIn(f"{self.file1_path}:1:apple", stdout) # Corrected line number test (was :0:apple)
        self.assertIn(f"{self.file1_path}:4:Apple", stdout) # Corrected line number test (was :3:Apple)
        self.assertIn(f"{self.file2_path}:2:Pineapple", stdout) # Corrected line number test (was :1:Pineapple)

    def test_file_not_found(self):
        non_existent_file = os.path.join(self.test_dir, "non_existent.txt")
        stdout, stderr, rc = self._run_cugrep("pattern", [non_existent_file])
        self.assertNotEqual(rc, 0)
        self.assertIn("Error reading", stderr)

    # The main.cpp output always includes line numbers by default, so -n is redundant.
    # The python CLI just passes it if present. A test for explicitly turning OFF
    # line numbers would require modifying main.cpp or cli.py to support a --no-line-numbers flag.
    # As per prompt, the C++ code has 'show_line_nums = true' by default in GrepOptions.
    def test_line_numbers_default_on(self):
        stdout, stderr, rc = self._run_cugrep("apple", [self.file1_path])
        self.assertEqual(rc, 0)
        self.assertIn("1:apple", stdout) # Corrected line number test (was 0:apple)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
