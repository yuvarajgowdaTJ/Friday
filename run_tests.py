import sys
import os
import pytest

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

def main():
    print("=" * 60)
    print("         J A R V I S   V 4   T E S T   S U I T E")
    print("=" * 60)
    
    exit_code = pytest.main(["tests/", "-v"])
    
    if exit_code == 0:
        print("\n[SUCCESS] All JARVIS V4 tests passed cleanly!")
        sys.exit(0)
    else:
        print("\n[FAIL] Test failures encountered.")
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
