"""
Rename slot_*.png files to font names and emit a JSON manifest with
category and multi-color flags.

Mapping is hand-built from visual inspection of the source PDF.
"""

from pathlib import Path
import json
import shutil

samples = Path(__file__).parent.parent / "samples"

# Layout per page, top-to-bottom by band, left then right.
# Each entry: (display_name, category, multi_color)
MAPPING = {
    1: [
        # band 1
        ("Wexford",  "Sans Serif", False), ("Block",     "Block",      False),
        # band 2
        ("Tricolor", "Block",      True),  ("Track",     "Block",      False),
        # band 3
        ("Maxwell",  "Block",      True),  ("Henry",     "Serif",      False),
        # band 4
        ("Better",   "Script",     False), ("Shadow",    "Display",    True),
        # band 5
        ("Windy",    "Script",     False), ("Cursive",   "Script",     False),
        # band 6
        ("Carambole","Sans Serif", False), ("Carsyn",    "Block",      True),
    ],
    2: [
        ("Charlie",  "Block",      False), ("Colin",     "Block",      True),
        ("Goodtime", "Script",     False), ("Casual",    "Script",     False),
        ("Dosido",   "Display",    False), ("Double",    "Script",     True),
        ("Satin",    "Script",     True),  ("Ella",      "Block",      True),
        ("Georgia",  "Serif",      False), ("Graham",    "Block",      False),
        ("Stitch",   "Specialty",  False), ("Swanky",    "Script",     False),
    ],
    3: [
        ("Harriet",  "Script",     False), ("Hoedown",   "Display",    True),
        ("Glitter",  "Script",     False), ("Loveme",    "Block",      False),
        ("Timely",   "Script",     False), ("Jordan",    "Script",     False),
        ("Kenzie",   "Script",     False), ("Joykate",   "Script",     False),
        ("Caroline", "Sans Serif", False), ("Collins",   "Script",     False),
        ("Pinkalicious","Sans Serif", False), ("Springs", "Script",   False),
    ],
    4: [
        ("Kathleen", "Script",     False), ("Layne",     "Block",      True),
        ("Duo",      "Block",      True),  ("Madeline",  "Script",     False),
        ("Madison",  "Block",      True),  ("Norma",     "Sans Serif", False),
        ("Pi B Pi (Greek)", "Monogram", False), ("Britain", "Sans Serif", False),
        ("Hannah",   "Script",     False), ("River",     "Block",      True),
        ("Mill",     "Block",      False), ("Outline",   "Block",      True),
    ],
    5: [
        ("Chalk",    "Block",      True),  ("Stitch (Cross)","Specialty", False),
        ("Sailor",   "Script",     False), ("Sport",     "Block",      True),
        ("Frannie",  "Script",     False), ("Barbie",    "Script",     False),
        ("Laura",    "Block",      True),  ("Debbie",    "Script",     False),
        ("Maple",    "Script",     False), ("Farmhouse", "Script",     False),
        ("Peace",    "Display",    False), ("PrettyThings","Script",   False),
    ],
}

manifest = []
for page, fonts in MAPPING.items():
    # 12 entries per page, alternating L/R per band
    for i, (name, cat, multi) in enumerate(fonts):
        band = i // 2 + 1
        col = "L" if i % 2 == 0 else "R"
        src = samples / f"slot_{page}_{band}_{col}.png"
        if not src.exists():
            print(f"MISSING: {src.name} ({name})")
            continue
        # safe filename
        safe = name.lower().replace("(", "").replace(")", "").replace(" ", "_")
        dst = samples / f"k_{safe}.png"
        shutil.copy(src, dst)
        manifest.append({
            "name": name,
            "category": cat,
            "multi_color": multi,
            "image": f"samples/k_{safe}.png",
            "source_slot": src.name,
        })

print(f"\nMapped {len(manifest)} fonts.")

# Write manifest
out = samples / "kristina_fonts.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print(f"Manifest -> {out}")

# Clean up slot_ files (keep only renamed k_ files)
removed = 0
for p in samples.glob("slot_*.png"):
    p.unlink()
    removed += 1
print(f"Removed {removed} slot_ files.")
