import os
import sys
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
TESTCASE_DIR = os.path.join(ROOT, "testcases")

def run_testcase(tc_name):
    tc_file = os.path.join(TESTCASE_DIR, f"{tc_name}.pnml")
    target = os.path.join(DATA, "example.pnml")

    if not os.path.exists(tc_file):
        print(f"Testcase not found: {tc_file}")
        sys.exit(1)

    print(f"\n=== Running Testcase: {tc_name} ===")

    shutil.copy(tc_file, target)
    print(f"Copied testcase to: {target}")

    subprocess.run(["python", os.path.join(ROOT, "run_all.py")], check=True)

    print("\n=== DONE ===\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_testcase.py tc_name")
        print("Example: python run_testcase.py tc3")
        sys.exit(0)

    tc_name = sys.argv[1]
    run_testcase(tc_name)
