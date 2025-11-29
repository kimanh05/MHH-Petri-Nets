import os
import json
import shutil
import subprocess

TESTCASE_DIR = "testcases_task2"
EXPECTED_FILE = "testcases_task2/expected_task2.json"
DATA_DIR = "data"

EXAMPLE_JSON = os.path.join(DATA_DIR, "net_structure.json")
OUTPUT_JSON = os.path.join(DATA_DIR, "reachable_markings.json")


def load_expected():
    with open(EXPECTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_marking(m):
    """Convert {P1:1,...} → tuple sorted by key."""
    keys = sorted(m.keys())
    return tuple(m[k] for k in keys)


def run_task2(testcase_path):
    """Copy testcase JSON → net_structure.json và chạy Task 2."""
    shutil.copy(testcase_path, EXAMPLE_JSON)

    # CHẠY TRỰC TIẾP TASK 2, KHÔNG QUA run_all.py
    subprocess.run(
        ["python", "task1_2_explicit/reachable_bfs.py"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {normalize_marking(m) for m in data}


def main():
    expected_all = load_expected()

    print("\n==============================")
    print("      RUNNING TASK 2 TESTS    ")
    print("==============================\n")

    passed = 0
    total = 0

    for file in sorted(os.listdir(TESTCASE_DIR)):
        if not file.startswith("tc_task2_") or not file.endswith(".json"):
            continue

        total += 1
        tc_name = file.replace(".json", "")
        tc_path = os.path.join(TESTCASE_DIR, file)

        expected_set = {
            normalize_marking(m)
            for m in expected_all[tc_name]
        }

        try:
            output_set = run_task2(tc_path)

            if output_set == expected_set:
                print(f"[PASS] {tc_name}")
                passed += 1
            else:
                print(f"[FAIL]  {tc_name}")

        except Exception as e:
            print(f"[ERROR] {tc_name}: {e}")

    print("\n==============================")
    print(f" Summary: {passed}/{total} PASSED")
    print("==============================\n")


if __name__ == "__main__":
    main()
