import os
import sys


def pytest_configure():
    # Ensure repo root is importable so `import modules.*` works in tests.
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root not in sys.path:
        sys.path.insert(0, root)

