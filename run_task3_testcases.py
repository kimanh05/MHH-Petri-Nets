import os
import json
import shutil
import subprocess

TESTCASE_DIR = "testcases_task3"       # nơi chứa .pnml
EXPECTED_FILE = "testcases_task3/expected_task3.json"  # file chứa expected
DATA_DIR = "data"                      # nơi run_all sẽ tạo output

def load_expected():
    with open(EXPECTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def run_task3_for_testcase(pnml_path):
    """
    Copy testcase → data/example.pnml
    Run Task 1–3 via run_all.py
    Read data/bdd_result.json
    Return num_markings
    """
    # copy pnml → data/example.pnml
    dst = os.path.join(DATA_DIR, "example.pnml")
    shutil.copy(pnml_path, dst)

    # run Task 1–3 (only Task 3 is used)
    print(f"\n=== Running Task 3 for: {os.path.basename(pnml_path)} ===")
    subprocess.run(["python", "run_all.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # load Task3 output
    output_file = os.path.join(DATA_DIR, "bdd_result.json")
    if not os.path.exists(output_file):
        print("❌ ERROR: Task 3 output not found!")
        return None

    result = json.load(open(output_file, "r", encoding="utf-8"))

    return result.get("num_markings")

def main():
    expected_dict = load_expected()
    print("\n==============================")
    print(" Running ALL Task 3 Testcases ")
    print("==============================\n")

    pnml_files = sorted(f for f in os.listdir(TESTCASE_DIR) if f.endswith(".pnml"))

    passed = 0

    for fname in pnml_files:
        testcase = fname.replace(".pnml", "")
        pnml_path = os.path.join(TESTCASE_DIR, fname)

        expected = expected_dict.get(testcase)
        if expected is None:
            print(f"[SKIP] {testcase} – missing expected result")
            continue

        expected_markings = expected["num_markings"]

        actual_markings = run_task3_for_testcase(pnml_path)

        if actual_markings is None:
            print(f"[FAIL] {testcase}: No output from Task 3")
            continue

        if actual_markings == expected_markings:
            print(f"[PASS] {testcase} → num_markings = {actual_markings}")
            passed += 1
        else:
            print(f"[FAIL] {testcase}: expected {expected_markings}, got {actual_markings}")

    print("\n==============================")
    print(f" Summary: {passed}/{len(pnml_files)} PASSED")
    print("==============================\n")

if __name__ == "__main__":
    main()
