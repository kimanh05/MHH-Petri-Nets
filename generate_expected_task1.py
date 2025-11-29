import os
import json
import xml.etree.ElementTree as ET

TESTCASE_DIR = "testcases_task1"
OUTPUT_FILE = os.path.join(TESTCASE_DIR, "expected_task1.json")


def parse_pnml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    ns = {"pnml": "http://www.pnml.org/version-2009/grammar/pnml"}

    places = []
    transitions = []
    arcs = []
    initial_marking = {}

    # places
    for place in root.findall(".//pnml:place", ns):
        pid = place.attrib.get("id")
        places.append(pid)

        imm = place.find("pnml:initialMarking/pnml:text", ns)
        if imm is not None:
            try:
                initial_marking[pid] = int(imm.text.strip())
            except:
                initial_marking[pid] = 0
        else:
            initial_marking[pid] = 0

    # transitions
    for transition in root.findall(".//pnml:transition", ns):
        transitions.append(transition.attrib.get("id"))

    # arcs
    for arc in root.findall(".//pnml:arc", ns):
        src = arc.attrib.get("source")
        tgt = arc.attrib.get("target")
        arcs.append([src, tgt])

    # sort
    places.sort()
    transitions.sort()
    arcs.sort()

    return {
        "places": places,
        "transitions": transitions,
        "arcs": arcs,
        "initial_marking": initial_marking
    }


def main():
    expected = {}

    for filename in sorted(os.listdir(TESTCASE_DIR)):
        if not filename.endswith(".pnml"):
            continue

        tc_name = filename.replace(".pnml", "")
        pnml_path = os.path.join(TESTCASE_DIR, filename)

        print(f"Parsing {filename} ...")
        expected[tc_name] = parse_pnml(pnml_path)

    # write JSON output into testcases_task1
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(expected, f, indent=4, ensure_ascii=False)

    print(f"\nDONE! Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
