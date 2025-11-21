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

import xml.etree.ElementTree as ET
import json
import os


class PetriNet:
    def __init__(self, filename: str):
        """Constructor – parse PNML file and build Petri net structure."""
        self.filename = filename
        self.places = {}
        self.transitions = {}
        self.arcs = []

        self._parse_pnml()

    def _parse_pnml(self):
        """Internal method: parse PNML XML and populate net components."""
        try:
            tree = ET.parse(self.filename)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.filename}")
        root = tree.getroot()

        for elem in root.iter():
            tag = elem.tag.split('}')[-1]  # handle namespaces

            if tag == "place":
                pid = elem.attrib.get("id")
                if not pid:
                    print("Warning: place without id")
                    continue

                mark_el = elem.find(".//{*}initialMarking/{*}text")
                marking = int(mark_el.text.strip()) if mark_el is not None else 0
                self.places[pid] = marking

            elif tag == "transition":
                tid = elem.attrib.get("id")
                if not tid:
                    print("⚠️ Warning: transition without id")
                    continue
                self.transitions[tid] = True

            elif tag == "arc":
                src = elem.attrib.get("source")
                tgt = elem.attrib.get("target")
                if not src or not tgt:
                    print(f"Warning: arc missing source or target ({src}->{tgt})")
                    continue
                self.arcs.append((src, tgt))

        self._validate_arcs()

    def _validate_arcs(self):
        """Check for missing or invalid arcs."""
        valid_arcs = []
        for (src, tgt) in self.arcs:
            if src not in self.places and src not in self.transitions:
                print(f"No arc between {src} and {tgt}: source not found")
                continue
            if tgt not in self.places and tgt not in self.transitions:
                print(f"No arc between {src} and {tgt}: target not found")
                continue
            if src in self.places and tgt in self.places:
                print(f"Arc connecting place {src} and place {tgt}")
                continue
            if src in self.transitions and tgt in self.transitions:
                print(f"Arc connecting transition {src} and transition {tgt}")
                continue
            valid_arcs.append([src, tgt])

        self.arcs = valid_arcs

    def to_dict(self):
        """Return the Petri net as a dictionary (for JSON export)."""
        return {
            "places": list(self.places.keys()),
            "transitions": list(self.transitions.keys()),
            "arcs": self.arcs,
            "initial_marking": self.places
        }

    def save_json(self, output_file: str):
        """Save Petri net structure to JSON file with exact required formatting."""
        net = self.to_dict()

        # --- Build JSON manually to ensure perfect formatting ---
        lines = []
        lines.append("{")

        # places in one line
        places_str = ", ".join(f"\"{p}\"" for p in net["places"])
        lines.append(f"    \"places\": [{places_str}],")

        # transitions in one line
        trans_str = ", ".join(f"\"{t}\"" for t in net["transitions"])
        lines.append(f"    \"transitions\": [{trans_str}],")

        # arcs block
        lines.append("    \"arcs\": [")
        for src, tgt in net["arcs"]:
            lines.append(f"        [\"{src}\", \"{tgt}\"] ,")
        # remove last comma
        lines[-1] = lines[-1].rstrip(" ,")
        lines.append("    ],")

        # initial_marking in one line
        im_items = ", ".join(f"\"{p}\": {m}" for p, m in net["initial_marking"].items())
        lines.append(f"    \"initial_marking\": {{{im_items}}}")

        lines.append("}")

        formatted = "\n".join(lines)

        # write file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted)

        print(f"\nDone! Petri net structure written to '{output_file}'.")

    def get_inputs(self, transition):
        """Return all input places of a given transition."""
        return [src for src, tgt in self.arcs if tgt == transition and src in self.places]

    def get_outputs(self, transition):
        """Return all output places of a given transition."""
        return [tgt for src, tgt in self.arcs if src == transition and tgt in self.places]

    def is_enabled(self, transition, marking):
        """Check if a transition is enabled under the given marking."""
        for p in self.get_inputs(transition):
            if marking.get(p, 0) == 0:
                return False
        return True

    def fire(self, transition, marking):
        """Fire a transition and return the new marking."""
        if not self.is_enabled(transition, marking):
            raise ValueError(f"Transition {transition} is not enabled.")

        new_marking = marking.copy()
        # remove tokens from input places
        for p in self.get_inputs(transition):
            new_marking[p] -= 1
        # add tokens to output places
        for p in self.get_outputs(transition):
            new_marking[p] += 1

        return new_marking

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "example.pnml")
    output_file = os.path.join(script_dir, "net_structure.json")

    net = PetriNet(input_file)
    net.save_json(output_file)

# run: python "C:\Users\ADMIN\Documents\Learning\UniDocs\Documents\HK251\MHH\Assigment 251\MHH-Petri-Nets-main\task1_2_explicit\pnml_parser.py"
