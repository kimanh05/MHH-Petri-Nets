import os
import shutil
import subprocess
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
TESTCASES = os.path.join(ROOT, "testcases")
EXPECTED = os.path.join(TESTCASES, "expected_results.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_pipeline(tc_name):
    src = os.path.join(TESTCASES, tc_name + ".pnml")
    dst = os.path.join(DATA, "example.pnml")

    if not os.path.exists(src):
        print(f"[ERROR] Testcase not found: {src}")
        return False

    shutil.copy(src, dst)

    try:
        subprocess.run(
            ["python", os.path.join(ROOT, "run_all.py")],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        return False

def validate(tc_name, expected):
    result_file = os.path.join(DATA, "deadlocks.json")
    if not os.path.exists(result_file):
        return False, "deadlocks.json missing"

    real = load_json(result_file)
    exp = expected[tc_name]

    # Compare deadlocks_found
    if real["deadlocks_found"] != exp["deadlocks_found"]:
        return False, f"deadlocks_found={real['deadlocks_found']} expected={exp['deadlocks_found']}"

    # Compare marking sets (exp may contain multiple valid)
    if exp["deadlock_states"]:
        real_state = real["deadlock_states"][0] if real["deadlock_states"] else None
        if real_state not in exp["deadlock_states"]:
            return False, "deadlock state mismatch"

    return True, ""

def main():
    expected = load_json(EXPECTED)

    testcases = list(expected.keys())

    print("\n==============================")
    print(" Running ALL 21 TESTCASES ")
    print("==============================\n")

    results = []

    for tc in testcases:
        print(f"--- Running {tc} ---")

        ok = run_pipeline(tc)
        if not ok:
            results.append((tc, "RUN FAIL"))
            print(f"[FAIL] Pipeline crashed for {tc}\n")
            continue

        valid, msg = validate(tc, expected)
        if valid:
            results.append((tc, "PASS"))
            print(f"[PASS] {tc}\n")
        else:
            results.append((tc, "FAIL"))
            print(f"[FAIL] {tc}: {msg}\n")

    print("\n==============================")
    print(" SUMMARY RESULTS (TC1–TC21) ")
    print("==============================\n")

    for tc, status in results:
        print(f"{tc:30}  {status}")

    print("\nDone.\n")


if __name__ == "__main__":
    main()
