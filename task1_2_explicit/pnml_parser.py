"""
Task 1 – Reading Petri Nets from PNML Files
--------------------------------------------
Description:
    Implements a parser that reads a 1-safe Petri net from a standard PNML file
    and constructs the internal representation of places, transitions, and arcs.
    The parser also verifies consistency (e.g., missing arcs or nodes).

Input:
    example.pnml

Output:
    net_structure.json

Author:
    Vinh Tien
"""

"""
Task 1 – Reading Petri Nets from PNML Files
--------------------------------------------
Description:
    Reads PNML and outputs net_structure.json into /data
"""

import xml.etree.ElementTree as ET
import json
import os
import sys


class PNMLFormatError(Exception):
    """Custom exception for invalid PNML format."""
    pass


class PetriNet:
    def __init__(self, filename: str):
        self.filename = filename
        self.places = {}
        self.transitions = {}
        self.arcs = []
        self._parse_pnml()

    # Parse PNML and extract nodes + arcs
    def _parse_pnml(self):
        if not os.path.exists(self.filename):
            raise PNMLFormatError(f"Error: PNML file not found: {self.filename}")

        try:
            tree = ET.parse(self.filename)
        except Exception as e:
            raise PNMLFormatError(f"Error: Cannot parse PNML (invalid XML): {e}")

        root = tree.getroot()

        for elem in root.iter():
            tag = elem.tag.split('}')[-1]

            # Place
            if tag == "place":
                pid = elem.attrib.get("id")
                if not pid:
                    raise PNMLFormatError("Error: A <place> element is missing an id.")

                mark_el = elem.find(".//{*}initialMarking/{*}text")
                marking = int(mark_el.text.strip()) if mark_el is not None else 0
                self.places[pid] = marking

            # Transition
            elif tag == "transition":
                tid = elem.attrib.get("id")
                if not tid:
                    raise PNMLFormatError("Error: A <transition> element is missing an id.")
                self.transitions[tid] = True

            # Arc
            elif tag == "arc":
                src = elem.attrib.get("source")
                tgt = elem.attrib.get("target")

                if not src or not tgt:
                    raise PNMLFormatError(
                        "Error: An <arc> element is missing source or target."
                    )

                self.arcs.append((src, tgt))

        self._validate_structure()
        self._validate_arcs()

    # Check node existence validity
    def _validate_structure(self):
        if len(self.places) == 0:
            raise PNMLFormatError("Error: PNML contains no places.")

        if len(self.transitions) == 0:
            # Allowed by assignment, but warn
            print("Warning: PNML contains no transitions.")

    # Validate arcs
    def _validate_arcs(self):
        valid_arcs = []

        for (src, tgt) in self.arcs:
            src_valid = src in self.places or src in self.transitions
            tgt_valid = tgt in self.places or tgt in self.transitions

            if not src_valid:
                raise PNMLFormatError(f"Error: Arc source '{src}' does not exist.")
            if not tgt_valid:
                raise PNMLFormatError(f"Error: Arc target '{tgt}' does not exist.")

            # forbidden arcs
            if src in self.places and tgt in self.places:
                raise PNMLFormatError(f"Error: Invalid arc place→place: {src} → {tgt}")

            if src in self.transitions and tgt in self.transitions:
                raise PNMLFormatError(
                    f"Error: Invalid arc transition→transition: {src} → {tgt}"
                )

            valid_arcs.append([src, tgt])

        self.arcs = valid_arcs

    # Convert to dictionary
    def to_dict(self):
        return {
            "places": list(self.places.keys()),
            "transitions": list(self.transitions.keys()),
            "arcs": self.arcs,
            "initial_marking": self.places
        }

    # Write JSON + print to terminal
    def save_json(self, output_file: str):
        data = self.to_dict()

        lines = []
        lines.append("{")

        # places
        places_str = ", ".join(f"\"{p}\"" for p in data["places"])
        lines.append(f"    \"places\": [{places_str}],")

        # transitions
        trans_str = ", ".join(f"\"{t}\"" for t in data["transitions"])
        lines.append(f"    \"transitions\": [{trans_str}],")

        # arcs
        lines.append("    \"arcs\": [")
        for src, tgt in data["arcs"]:
            lines.append(f"        [\"{src}\", \"{tgt}\"] ,")
        if len(data["arcs"]) > 0:
            lines[-1] = lines[-1].rstrip(" ,")
        lines.append("    ],")

        im_str = ", ".join(f"\"{p}\": {m}" for p, m in data["initial_marking"].items())
        lines.append(f"    \"initial_marking\": {{{im_str}}}")

        lines.append("}")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("\n".join(lines))

if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA = os.path.join(ROOT, "data")
    os.makedirs(DATA, exist_ok=True)

    input_file = os.path.join(DATA, "example.pnml")
    output_file = os.path.join(DATA, "net_structure.json")

    try:
        net = PetriNet(input_file)
        net.save_json(output_file)
    except PNMLFormatError as e:
        print(str(e))
        sys.exit(1)