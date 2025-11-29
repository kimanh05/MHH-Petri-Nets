import os
import json
import shutil
import subprocess

TESTCASE_DIR = "testcases_task1"
EXPECTED_FILE = "testcases_task1/expected_task1.json"
DATA_DIR = "data"

EXAMPLE_PNML = os.path.join(DATA_DIR, "example.pnml")
OUTPUT_JSON = os.path.join(DATA_DIR, "net_structure.json")


def load_expected():
    with open(EXPECTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_arcs(arcs):
    return sorted([tuple(a) for a in arcs])


def run_task1_for_testcase(pnml_path):
    """
    Copy testcase → data/example.pnml
    Run only Task 1 parser
    Return parsed dict
    """

    # copy input
    shutil.copy(pnml_path, EXAMPLE_PNML)

    # run task1 parser
    result = subprocess.run(
        ["python", "task1_2_explicit/pnml_parser.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Check output file
    if not os.path.exists(OUTPUT_JSON):
        return None

    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["arcs"] = normalize_arcs(data.get("arcs", []))

    return {
        "places": sorted(data.get("places", [])),
        "transitions": sorted(data.get("transitions", [])),
        "arcs": data["arcs"],
        "initial_marking": data.get("initial_marking", {})
    }


def compare(expected, result):
    return (
        sorted(expected["places"]) == sorted(result["places"]) and
        sorted(expected["transitions"]) == sorted(result["transitions"]) and
        normalize_arcs(expected["arcs"]) == normalize_arcs(result["arcs"]) and
        expected["initial_marking"] == result["initial_marking"]
    )


def main():
    expected_all = load_expected()

    print("\n==============================")
    print("      RUNNING TASK 1 TESTS    ")
    print("==============================\n")

    pnml_files = sorted([f for f in os.listdir(TESTCASE_DIR) if f.endswith(".pnml")])

    passed = 0

    for fname in pnml_files:
        testname = fname.replace(".pnml", "")
        pnml_path = os.path.join(TESTCASE_DIR, fname)

        expected = expected_all.get(testname)
        if expected is None:
            print(f"[SKIP] {testname} – missing expected")
            continue

        expected["arcs"] = normalize_arcs(expected["arcs"])

        result = run_task1_for_testcase(pnml_path)

        if result is None:
            print(f"[FAIL] {testname}: No output from Task 1\n")
            continue

        if compare(expected, result):
            print(f"[PASS] {testname}\n")
            passed += 1
        else:
            print(f"[FAIL] {testname}\n")

    print("==============================")
    print(f" Summary: {passed}/{len(pnml_files)} PASSED")
    print("==============================\n")


if __name__ == "__main__":
    main()
