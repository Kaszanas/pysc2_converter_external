import os
import sys

import pytest

if __name__ == "__main__":
    """
    Utility script to run pytest programmatically.
    This makes it very easy to attach a debugger (like the VS Code Python Debugger)
    by simply running this file in 'Debug' mode (F5).
    """
    # Get the directory of this script (the `tests` directory)
    tests_dir = os.path.dirname(os.path.abspath(__file__))

    # Run pytest programmatically
    # -s: disable capturing of stdout/stderr (useful for debugging)
    # -v: verbose output
    # Note: To drop into the built-in python terminal debugger on failure,
    # you can add "--pdb" to the list below.
    args = ["-s", "-v", tests_dir]

    print(f"Running pytest with args: {args}")
    sys.exit(pytest.main(args))
