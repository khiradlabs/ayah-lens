#!/usr/bin/env python3
"""Generate the full verbatim Arabic/Pickthall bundle from the prepared sources."""
import argparse
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
args = parser.parse_args()

def read(name):
    result = {}
    for line in (args.source / name).read_text().splitlines():
        if re.match(r"^\d+\|\d+\|", line):
            surah, ayah, text = line.split("|", 2)
            identifier = f"{int(surah)}:{int(ayah)}"
            assert identifier not in result and text
            result[identifier] = text
    return result

arabic, english = read("quran-uthmani.txt"), read("en.pickthall.txt")
assert len(arabic) == 6236 and arabic.keys() == english.keys()
assert {int(key.split(":")[0]) for key in arabic} == set(range(1, 115))
rows = [{"id": key, "arabic": text, "translation": english[key]} for key, text in arabic.items()]
root = Path(__file__).resolve().parents[1]
destination = root / "App/Resources/verses.json"
destination.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
for row in json.loads(destination.read_text()):
    assert row["arabic"] == arabic[row["id"]] and row["translation"] == english[row["id"]]
print("PASS: bundled 6,236 aligned, verbatim Arabic/Pickthall ayahs across 114 surahs")
