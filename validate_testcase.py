import os
import sys
import json
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
TESTCASES = os.path.join(ROOT, "testcases")
EXPECTED = os.path.join(TESTCASES, "expected_results.json")

def run_pipeline(tc_name):
    tc_file = os.path.join(TESTCASES, f"{tc_name}.pnml")
    if not os.path.exists(tc_file):
        print(f"Testcase not found: {tc_file}")
        sys.exit(1)

    # Copy PNML to data/example.pnml
    shutil.copy(tc_file, os.path.join(DATA, "example.pnml"))

    # Run pipeline
    subprocess.run(["python", os.path.join(ROOT, "run_all.py")], check=True)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate(tc_name):
    expected = load_json(EXPECTED)

    if tc_name not in expected:
        print(f"No expected result for {tc_name}")
        return

    exp_deadlock = expected[tc_name]

    result_file = os.path.join(DATA, "deadlocks.json")
    if not os.path.exists(result_file):
        print("Error: deadlocks.json not generated.")
        return

    real = load_json(result_file)

    # Compare only deadlock info
    if real["deadlocks_found"] != exp_deadlock["deadlocks_found"]:
        print(f"FAIL: expected deadlocks_found={exp_deadlock['deadlocks_found']}, got {real['deadlocks_found']}")
        return

    if exp_deadlock["deadlock_states"]:
        # expected could have multiple possible correct answers
        real_state = real["deadlock_states"][0] if real["deadlock_states"] else None

        if real_state not in exp_deadlock["deadlock_states"]:
            print(f"FAIL: deadlock state mismatch.\nExpected one of: {exp_deadlock['deadlock_states']}\nGot: {real_state}")
            return

    print(f"PASS: {tc_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_testcase.py tc3")
        sys.exit(0)

    tc = sys.argv[1]

    run_pipeline(tc)
    validate(tc)
