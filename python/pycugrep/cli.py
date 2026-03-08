
import argparse
import subprocess
import os
import sys
from importlib.resources import files as importlib_files

def main():
    parser = argparse.ArgumentParser(
        description="A GPU-accelerated grep tool."
    )
    parser.add_argument("pattern", help="The regex pattern to search for.")
    parser.add_argument("files", nargs='+', help="Files to search in.")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="Ignore case distinctions.")
    parser.add_argument("-c", "--count-only", action="store_true",
                        help="Count matching lines only.")
    parser.add_argument("-v", "--invert-match", action="store_true",
                        help="Invert match (show non-matching lines).")
    parser.add_argument("-n", "--show-line-nums", action="store_true",
                        help="Show line numbers (default: on).")
    args = parser.parse_args()

    # Dynamically locate the cugrep binary using importlib.resources
    try:
        cugrep_path_obj = importlib_files('pycugrep').joinpath('bin', 'cugrep')
        cugrep_executable = str(cugrep_path_obj)
        if not os.path.exists(cugrep_executable):
            raise FileNotFoundError(f"cugrep executable not found at {cugrep_executable}")
    except Exception as e:
        print(f"Error locating cugrep executable: {e}", file=sys.stderr)
        print("Please ensure 'pycugrep' is correctly installed and the binary exists.", file=sys.stderr)
        sys.exit(1)

    cugrep_command = [cugrep_executable]
    if args.ignore_case:    cugrep_command.append("-i")
    if args.count_only:     cugrep_command.append("-c")
    if args.invert_match:   cugrep_command.append("-v")
    if args.show_line_nums: cugrep_command.append("-n") # This is default for cugrep, but good to pass explicitly

    cugrep_command.append(args.pattern)
    cugrep_command.extend(args.files)

    # Set LD_LIBRARY_PATH dynamically if it's not already set, or append
    # This assumes libkvikio might be needed at runtime by the C++ executable
    # and its path could be in a specific Python package location.
    # This part might need further refinement based on the exact deployment of libkvikio.
    env = os.environ.copy()
    try:
        kvikio_lib_path_candidate = str(importlib_files('libkvikio').joinpath('lib64'))
        if os.path.exists(kvikio_lib_path_candidate):
            current_ld_library_path = env.get('LD_LIBRARY_PATH', '')
            if kvikio_lib_path_candidate not in current_ld_library_path:
                env['LD_LIBRARY_PATH'] = f"{kvikio_lib_path_candidate}:{current_ld_library_path}"
                # print(f"cli.py: Set LD_LIBRARY_PATH to: {env['LD_LIBRARY_PATH']}", file=sys.stderr) # Debug print
    except Exception:
        # print(f"cli.py: Warning: libkvikio path could not be determined.", file=sys.stderr) # Debug print
        pass # libkvikio might not be installed, proceed without setting LD_LIBRARY_PATH for it.

    try:
        # print(f"cli.py: Executing C++ cugrep: {cugrep_command}", file=sys.stderr) # Debug print
        result = subprocess.run(cugrep_command, capture_output=True, text=True, check=True, env=env)
        print(result.stdout, end="")
        sys.exit(0) # Explicitly exit 0 on success
    except subprocess.CalledProcessError as e:
        # print(f"cli.py: Caught CalledProcessError. C++ cugrep exit code: {e.returncode}", file=sys.stderr) # Debug print
        print(f"Error executing cugrep: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError as e:
        print(f"Error: cugrep executable not found or path issue: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
